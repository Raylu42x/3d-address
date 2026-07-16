import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
"""
tests_edge.py — edge-case probes for the Phase 1 core.

Report-style: every check prints PASS/FAIL and the run continues. The goal is to
pin down EXACT behavior at the hard edges (shell surfaces, poles, the antimeridian
seam, cell boundaries, out-of-range inputs), not just to confirm no crashes.

    python tests_edge.py
"""

import math
from protocol.geometry import (
    INNER, OUTER, R_MEAN, CELL1, N1, HALF, geo_to_xyz, xyz_to_geo,
)
from protocol.encoder import encode, decode, bounds_xyz

_pass = 0
_fail = 0
def check(name, cond, detail=""):
    global _pass, _fail
    _pass += bool(cond); _fail += (not cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  —  {detail}" if detail else ""))

def err_m(lat, lon, alt, dlat, dlon, dalt):
    x1,y1,z1 = geo_to_xyz(lat,lon,alt); x2,y2,z2 = geo_to_xyz(dlat,dlon,dalt)
    return math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)*1000.0

def contained(idx, lat, lon, alt, eps=1e-6):
    x0,x1,y0,y1,z0,z1 = bounds_xyz(idx); x,y,z = geo_to_xyz(lat,lon,alt)
    return (x0-eps<=x<=x1+eps and y0-eps<=y<=y1+eps and z0-eps<=z<=z1+eps)

# ---------------------------------------------------------------------------
print("\n1. SHELL RADIAL BOUNDARIES  (intended: inclusive [INNER, OUTER])")
# exact inner surface (alt = -13) and outer ceiling (alt = +2000), many angles
for tag, alt in [("inner surface alt=-13", -13.0), ("outer ceiling alt=+2000", 2000.0)]:
    flipped = []
    for lat in (-89, -45, -1, 0, 1, 45, 89):
        for lon in (-179, -90, -1, 0, 1, 90, 179):
            if encode(lat, lon, alt, 5) is None:
                flipped.append((lat, lon))
    check(f"{tag}: all 49 angles valid", len(flipped) == 0,
          "none flipped to None" if not flipped else f"{len(flipped)} flipped to None, e.g. {flipped[:3]}")

# just inside / just outside
check("alt=-12.99 (just inside) valid",  encode(0,0,-12.99,5) is not None)
check("alt=+1999.99 (just inside) valid", encode(0,0,1999.99,5) is not None)
check("alt=-13.01 (just outside) -> None", encode(0,0,-13.01,5) is None)
check("alt=+2000.01 (just outside) -> None", encode(0,0,2000.01,5) is None)

# ---------------------------------------------------------------------------
print("\n2. DEGENERATE / OUT-OF-RANGE RADIUS")
check("Earth's core (alt=-6371) -> None", encode(0,0,-6371,5) is None, "r=0, no crash")
check("deep space (alt=5000) -> None", encode(0,0,5000,5) is None)
# sign-flip probe: r = R_MEAN + alt goes negative
mirror = encode(0,0,-12742,5)   # r intended = -6371
check("alt=-12742 (negative radius) -> None", mirror is None,
      "expected None" if mirror is None else f"LEAK: returned {mirror} (antipodal mirror)")

# ---------------------------------------------------------------------------
print("\n3. POLES  (longitude is degenerate; position must still be exact)")
for tag, lat in [("North Pole", 90.0), ("South Pole", -90.0)]:
    idx = encode(lat, 0.0, 0.0, 5)
    ok = idx is not None
    detail = ""
    if ok:
        (dlat, dlon, dalt), edge = decode(idx)
        e = err_m(lat, 0.0, 0.0, dlat, dlon, dalt)
        ok = e <= edge*1000*math.sqrt(3)/2 + 1e-6
        detail = f"recovered lat={dlat:.4f}, lon={dlon:.4f} (degenerate), err={e:.2f}m"
    check(f"{tag} round-trips in cell", ok, detail)

# ---------------------------------------------------------------------------
print("\n4. ANTIMERIDIAN SEAM  (lon=+180 vs lon=-180 = same physical point)")
a = encode(0.0, 180.0, 0.0, 5)
b = encode(0.0, -180.0, 0.0, 5)
samept = err_m(0,180,0, 0,-180,0)  # geo distance between the two inputs
check("both encode (not None)", a is not None and b is not None)
check("inputs are the same physical point", samept < 1e-3, f"separation {samept:.2e} m")
check("indices identical across the seam", a == b,
      "same address" if a == b else f"DIFFER: {a} vs {b}  (point sits on a cell seam)")

# ---------------------------------------------------------------------------
print("\n5. OUT-OF-RANGE ANGLES  (silently remapped, not rejected)")
over_lon = encode(0.0, 181.0, 0.0, 5)
equiv    = encode(0.0, -179.0, 0.0, 5)
check("lon=181 == lon=-179", over_lon == equiv,
      "remapped onto -179" if over_lon == equiv else f"{over_lon} vs {equiv}")
over_lat = encode(100.0, 0.0, 0.0, 5)   # lat>90
check("lat=100 still encodes (no validation)", over_lat is not None,
      "input lat not range-checked" if over_lat is not None else "rejected")

# ---------------------------------------------------------------------------
print("\n6. WORD-COUNT EXTREMES")
one = encode(51.5074, -0.1278, 0.1, 1)
check("words=1 returns single index", one is not None and len(one) == 1, f"{one}")
if one:
    (_,_,_), edge1 = decode(one)
    check("words=1 cell ~= level-1 cell (414.63 km)", abs(edge1-CELL1) < 1e-6, f"edge={edge1:.2f} km")
eight = encode(51.5074, -0.1278, 0.1, 8)
ok8 = eight is not None and len(eight) == 8 and contained(eight, 51.5074, -0.1278, 0.1)
if eight:
    (_,_,_), edge8 = decode(eight)
    check("words=8 round-trips & contained", ok8, f"cell={edge8*1e6:.3f} mm")
try:
    encode(0,0,0,0); raised = False
except ValueError:
    raised = True
check("words=0 raises ValueError", raised)

# ---------------------------------------------------------------------------
print("\n7. DETERMINISM & EXACT-AXIS POINTS")
p1 = encode(40.0, 40.0, 100.0, 6); p2 = encode(40.0, 40.0, 100.0, 6)
check("same input -> identical output", p1 == p2)
check("equator+prime-meridian (0,0) encodes", encode(0,0,0,5) is not None)
# point exactly on the London +Y axis: x=0, z=0
idxY = encode(0.0, 0.0, 0.0, 5)
check("on +Y axis (London) contained", idxY is not None and contained(idxY,0,0,0))

# ---------------------------------------------------------------------------
print("\n8. NEAR-SURFACE CONTAINMENT SWEEP")
bad = 0; tested = 0
for lat in range(-80, 81, 20):
    for lon in range(-180, 180, 30):
        for alt in (-12.9, 0.0, 1999.0):
            idx = encode(lat, lon, alt, 6)
            if idx is None: continue
            tested += 1
            if not contained(idx, lat, lon, alt): bad += 1
check(f"all near-surface points contained ({tested} tested)", bad == 0,
      "0 escapes" if bad == 0 else f"{bad} points outside their cell")

# ---------------------------------------------------------------------------
print(f"\nSUMMARY: {_pass} passed, {_fail} failed")