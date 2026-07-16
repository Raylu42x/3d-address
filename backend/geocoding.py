"""
geocoding.py — street-address <-> coordinate helpers.

Thin proxies over public OpenStreetMap services:
  - Nominatim for forward (/geocode) and reverse (/reverse) geocoding
  - Photon for search-as-you-type autocomplete (/geocode_suggest)

These are the only endpoints that reach the network. They are gated by
GEOCODER_ENABLED and rate-limited (see config), because the upstreams publish
strict usage policies. All upstream URLs come from config, never hardcoded.
"""
import httpx
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

import config
from ratelimit import limit

router = APIRouter(tags=["geocoding"])


def _require_geocoder():
    if not config.GEOCODER_ENABLED:
        return JSONResponse(
            status_code=503,
            content={"ok": False, "error": "geocoding is disabled on this server"},
        )
    return None


def _headers():
    return {"User-Agent": config.GEO_USER_AGENT}


@router.get("/geocode")
@limit(config.RATE_LIMIT_GEOCODE)
def geocode(request: Request, q: str = Query(..., min_length=1, max_length=200)):
    """Street address / place name -> coordinates."""
    off = _require_geocoder()
    if off:
        return off
    try:
        r = httpx.get(f"{config.NOMINATIM_URL}/search",
                      params={"q": q, "format": "json", "limit": 1},
                      headers=_headers(), timeout=config.GEO_TIMEOUT)
        data = r.json()
    except Exception:
        return JSONResponse(status_code=502, content={"ok": False, "error": "geocoder unavailable"})
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "no match for that address"})
    top = data[0]
    return {"ok": True, "lat": float(top["lat"]), "lon": float(top["lon"]),
            "display_name": top.get("display_name", "")}


@router.get("/geocode_suggest")
@limit(config.RATE_LIMIT_GEOCODE)
def geocode_suggest(request: Request, q: str = Query(..., min_length=1, max_length=200)):
    """Autocomplete: search-as-you-type via Photon (built for partial queries,
    unlike Nominatim which needs complete words)."""
    off = _require_geocoder()
    if off:
        return off
    try:
        r = httpx.get(f"{config.PHOTON_URL}/api/",
                      params={"q": q, "limit": 5},
                      headers=_headers(), timeout=config.GEO_TIMEOUT)
        feats = r.json().get("features", [])
    except Exception:
        return {"ok": False, "results": []}
    results = []
    for f in feats:
        p = f.get("properties", {})
        name = ", ".join(x for x in [p.get("name"), p.get("street"), p.get("city"),
                                     p.get("state"), p.get("country")] if x)
        lon, lat = f["geometry"]["coordinates"][:2]
        results.append({"display_name": name, "lat": str(lat), "lon": str(lon)})
    return {"ok": True, "results": results}


@router.get("/reverse")
@limit(config.RATE_LIMIT_GEOCODE)
def reverse(request: Request, lat: float, lon: float):
    """Coordinates -> nearest street address."""
    off = _require_geocoder()
    if off:
        return off
    try:
        r = httpx.get(f"{config.NOMINATIM_URL}/reverse",
                      params={"lat": lat, "lon": lon, "format": "json"},
                      headers=_headers(), timeout=config.GEO_TIMEOUT)
        data = r.json()
    except Exception:
        return JSONResponse(status_code=502, content={"ok": False, "error": "geocoder unavailable"})
    return {"ok": True, "display_name": data.get("display_name", "")}
