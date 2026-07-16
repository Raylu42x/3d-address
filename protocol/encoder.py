"""
encoder.py — Phase 1 numeric encoder / decoder.

Converts between geographic coordinates and a list of cell indices ("word indices",
before the dictionary layer). The first index is a level-1 cell (0..25,459); each
further index is a 30^3 child (0..26,999).

    idx   = encode(lat, lon, alt_km, words=5)
    geo, edge_km = decode(idx)

No dictionary or checksum here — those are Phase 4/5. This is the pure spatial core.
"""

from .geometry import (
    N1, SUB, HALF, CELL1, INNER, OUTER, R_MEAN, geo_to_xyz, xyz_to_geo,
)
from .carve import build_valid_table

# Build the level-1 table once at import.
_VALID, _RAW2WORD, _WORD2RAW = build_valid_table()


def valid_cell_count():
    return len(_WORD2RAW)


def _cell1_bounds(ix, iy, iz):
    return (
        -HALF + ix * CELL1, -HALF + (ix + 1) * CELL1,
        -HALF + iy * CELL1, -HALF + (iy + 1) * CELL1,
        -HALF + iz * CELL1, -HALF + (iz + 1) * CELL1,
    )


def encode(lat, lon, alt_km, words=5):
    """
    Encode a geographic point to a list of `words` cell indices.
    Returns None if the point lies outside the addressable shell.
    """
    if words < 1:
        raise ValueError("words must be >= 1")

    # the point must lie within the shell band. Gate on the intended radius
    # (R_MEAN + alt) BEFORE building XYZ, so an absurd altitude that drives the
    # radius negative is rejected outright rather than aliased onto its
    # antipodal mirror by the lost sign. This is also exact at the boundary
    # (no sqrt round-trip), so alt=-13 / alt=+2000 stay cleanly inclusive.
    r = R_MEAN + alt_km
    if r < INNER or r > OUTER:
        return None

    x, y, z = geo_to_xyz(lat, lon, alt_km)
    ix = min(N1 - 1, max(0, int((x + HALF) // CELL1)))
    iy = min(N1 - 1, max(0, int((y + HALF) // CELL1)))
    iz = min(N1 - 1, max(0, int((z + HALF) // CELL1)))

    w1 = int(_RAW2WORD[ix, iy, iz])
    if w1 < 0:
        return None  # outside the shell

    out = [w1]
    x0, x1, y0, y1, z0, z1 = _cell1_bounds(ix, iy, iz)
    for _ in range(words - 1):
        sx = (x1 - x0) / SUB; sy = (y1 - y0) / SUB; sz = (z1 - z0) / SUB
        cx = min(SUB - 1, max(0, int((x - x0) // sx)))
        cy = min(SUB - 1, max(0, int((y - y0) // sy)))
        cz = min(SUB - 1, max(0, int((z - z0) // sz)))
        out.append((SUB - 1 - cz) * SUB * SUB + cy * SUB + cx)
        x0, x1 = x0 + cx * sx, x0 + (cx + 1) * sx
        y0, y1 = y0 + cy * sy, y0 + (cy + 1) * sy
        z0, z1 = z0 + cz * sz, z0 + (cz + 1) * sz
    return out


def decode(idx):
    """
    Decode a list of cell indices to (center_geo, cell_edge_km).
    center_geo = (lat, lon, alt_km) of the final cell's center.
    """
    ix, iy, iz = _WORD2RAW[idx[0]]
    x0, x1, y0, y1, z0, z1 = _cell1_bounds(ix, iy, iz)
    for w in idx[1:]:
        cztop = w // (SUB * SUB)
        rem = w % (SUB * SUB)
        cy = rem // SUB
        cx = rem % SUB
        cz = SUB - 1 - cztop
        sx = (x1 - x0) / SUB; sy = (y1 - y0) / SUB; sz = (z1 - z0) / SUB
        x0, x1 = x0 + cx * sx, x0 + (cx + 1) * sx
        y0, y1 = y0 + cy * sy, y0 + (cy + 1) * sy
        z0, z1 = z0 + cz * sz, z0 + (cz + 1) * sz
    center = xyz_to_geo((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    return center, (x1 - x0)


def bounds_xyz(idx):
    """Return the final cell's XYZ bounding box (x0,x1,y0,y1,z0,z1) in km."""
    ix, iy, iz = _WORD2RAW[idx[0]]
    x0, x1, y0, y1, z0, z1 = _cell1_bounds(ix, iy, iz)
    for w in idx[1:]:
        cztop = w // (SUB * SUB); rem = w % (SUB * SUB)
        cy = rem // SUB; cx = rem % SUB; cz = SUB - 1 - cztop
        sx = (x1 - x0) / SUB; sy = (y1 - y0) / SUB; sz = (z1 - z0) / SUB
        x0, x1 = x0 + cx * sx, x0 + (cx + 1) * sx
        y0, y1 = y0 + cy * sy, y0 + (cy + 1) * sy
        z0, z1 = z0 + cz * sz, z0 + (cz + 1) * sz
    return (x0, x1, y0, y1, z0, z1)