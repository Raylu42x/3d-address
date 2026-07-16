"""
geometry.py — constants and coordinate conversions for the 3D address protocol.

Frame (Earth-Centered, fixed):
    +Z -> North Pole
    +Y -> 0 deg longitude at the equator (London meridian)
    +X -> 90 deg E at the equator
All distances in kilometers; angles in degrees at the public API.
"""

import math

# --- bounding volume ---
CUBE   = 17000.0          # cube width (km)
HALF   = CUBE / 2.0       # 8500 km
R_MEAN = 6371.0           # mean Earth radius (altitude reference)
INNER  = 6358.0           # R_MEAN - 13 km  (~8 miles below surface)
OUTER  = 8371.0           # R_MEAN + 2000 km (LEO ceiling)

# --- grid ---
N1   = 41                 # level-1 cells per edge (41^3 = 68,921)
SUB  = 30                 # subdivision factor per added word (30^3 = 27,000)
CELL1 = CUBE / N1         # level-1 cell edge (km)

DICT_SIZE = SUB ** 3      # 27,000


def geo_to_xyz(lat_deg, lon_deg, alt_km):
    """(latitude, longitude, altitude_km) -> (X, Y, Z) in km."""
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    r = R_MEAN + alt_km
    return (
        r * math.cos(lat) * math.sin(lon),   # X (90 E)
        r * math.cos(lat) * math.cos(lon),   # Y (London)
        r * math.sin(lat),                   # Z (north)
    )


def xyz_to_geo(x, y, z):
    """(X, Y, Z) in km -> (latitude, longitude, altitude_km)."""
    r = math.sqrt(x * x + y * y + z * z)
    lat = math.degrees(math.asin(z / r))
    lon = math.degrees(math.atan2(x, y))
    return (lat, lon, r - R_MEAN)


def cell_distance_range(lo, hi):
    """Nearest and farthest |coord| to 0 for an interval [lo, hi] on one axis."""
    near = 0.0 if (lo <= 0 <= hi) else min(abs(lo), abs(hi))
    far = max(abs(lo), abs(hi))
    return near, far
