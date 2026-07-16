import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
"""
tests.py — round-trip and property tests for the Phase 1 core.

    python tests.py
"""

import math
import random
from protocol.geometry import geo_to_xyz, INNER, OUTER, R_MEAN
from protocol.encoder import encode, decode, bounds_xyz, valid_cell_count


def _err_m(lat, lon, alt, dlat, dlon, dalt):
    x1, y1, z1 = geo_to_xyz(lat, lon, alt)
    x2, y2, z2 = geo_to_xyz(dlat, dlon, dalt)
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) * 1000.0


def test_known_points():
    cases = [
        ("London", 51.5074, -0.1278, 0.1),
        ("New York", 40.7128, -74.0060, 0.05),
        ("Sydney", -33.8688, 151.2093, 0.02),
        ("North Pole", 89.9, 0.0, 0.0),
        ("ISS-ish", 0.0, 120.0, 420.0),
        ("Quito hi-alt", -0.18, -78.47, 2.8),
    ]
    print("round-trip (5 words):")
    all_ok = True
    for name, lat, lon, alt in cases:
        idx = encode(lat, lon, alt, 5)
        assert idx is not None, f"{name} unexpectedly outside shell"
        (dlat, dlon, dalt), edge = decode(idx)
        err = _err_m(lat, lon, alt, dlat, dlon, dalt)
        within = err <= edge * 1000 * math.sqrt(3) / 2 + 1e-6
        all_ok &= within
        print(f"  {name:14} err={err:6.2f} m  cell={edge*1000:6.2f} m  {'OK' if within else 'FAIL'}")
    assert all_ok
    print("  -> all within final cell\n")


def test_random_points(n=20000):
    """Random points inside the shell must round-trip within the final cell."""
    rng = random.Random(42)
    fails = 0
    for _ in range(n):
        lat = math.degrees(math.asin(rng.uniform(-1, 1)))
        lon = rng.uniform(-180, 180)
        alt = rng.uniform(-12, 1999)  # safely inside the shell
        idx = encode(lat, lon, alt, 6)
        if idx is None:
            continue
        x0, x1, y0, y1, z0, z1 = bounds_xyz(idx)
        x, y, z = geo_to_xyz(lat, lon, alt)
        inside = (x0 - 1e-6 <= x <= x1 + 1e-6 and
                  y0 - 1e-6 <= y <= y1 + 1e-6 and
                  z0 - 1e-6 <= z <= z1 + 1e-6)
        if not inside:
            fails += 1
    print(f"random containment ({n:,} pts, 6 words): {n - fails:,} inside, {fails} failures")
    assert fails == 0


def test_outside_shell():
    """Points clearly outside the shell return None."""
    deep = encode(0.0, 0.0, -100.0, 5)      # 100 km underground
    space = encode(0.0, 0.0, 3000.0, 5)     # well above LEO ceiling
    print(f"outside-shell handling: underground={deep}, deep-space={space}")
    assert deep is None and space is None


if __name__ == "__main__":
    print(f"valid level-1 cells: {valid_cell_count():,}\n")
    test_known_points()
    test_random_points()
    test_outside_shell()
    print("\nall tests passed.")
