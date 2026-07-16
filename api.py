"""
api.py — REST service for the 3D word-address protocol.

Run:
    pip install fastapi uvicorn
    uvicorn api:app --reload
    open http://127.0.0.1:8000        (web UI)
    open http://127.0.0.1:8000/docs   (interactive API docs)

Endpoints:
    POST /encode  {lat, lon, alt_km, words, format}  -> address
    POST /decode  {address}                          -> location
    GET  /health
    GET  /                                           -> web UI
"""
import os
import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

import address as A
import dictionary as D

app = FastAPI(title="3D Word-Based Address Protocol", version="0.2")

HERE = os.path.dirname(__file__)

# --- geocoding (OpenStreetMap Nominatim; be gentle: ~1 request/second) ---
NOMINATIM = "https://nominatim.openstreetmap.org"
GEO_HEADERS = {"User-Agent": "WordAddressProtocol/0.2 (prototype)"}


class EncodeReq(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    alt_km: float = 0.0
    words: int = Field(5, ge=1, le=8)
    format: str = "words"          # "words" | "transfer" | "all"


class DecodeReq(BaseModel):
    address: str


@app.get("/health")
def health():
    return {"ok": True, "dictionary_source": D.SOURCE, "words": len(D.WORD_LIST)}


@app.post("/encode")
def encode(r: EncodeReq):
    try:
        full = A.encode_all(r.lat, r.lon, r.alt_km, r.words)
    except ValueError as e:
        return JSONResponse(status_code=422, content={"ok": False, "error": str(e)})
    if full is None:
        return JSONResponse(status_code=422,
                            content={"ok": False, "error": "point is outside the addressable shell "
                                     "(valid altitude is -13 km to +2,000 km)"})
    if r.format == "words":
        return {"ok": True, "address": full["words"], **full}
    if r.format == "transfer":
        return {"ok": True, "address": full["transfer"], **full}
    return {"ok": True, **full}


@app.post("/decode")
def decode(r: DecodeReq):
    res = A.decode(r.address)
    status = 200 if res.get("valid") else 422
    return JSONResponse(status_code=status, content={"ok": res.get("valid", False), **res})


@app.get("/geocode")
def geocode(q: str):
    """Street address / place name -> coordinates."""
    try:
        r = httpx.get(f"{NOMINATIM}/search",
                      params={"q": q, "format": "json", "limit": 1},
                      headers=GEO_HEADERS, timeout=8.0)
        data = r.json()
    except Exception:
        return JSONResponse(status_code=502, content={"ok": False, "error": "geocoder unavailable"})
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "no match for that address"})
    top = data[0]
    return {"ok": True, "lat": float(top["lat"]), "lon": float(top["lon"]),
            "display_name": top.get("display_name", "")}


@app.get("/geocode_suggest")
def geocode_suggest(q: str):
    """Autocomplete: search-as-you-type via Photon (built for partial queries,
    unlike Nominatim which needs complete words)."""
    try:
        r = httpx.get("https://photon.komoot.io/api/",
                      params={"q": q, "limit": 5},
                      headers=GEO_HEADERS, timeout=6.0)
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


@app.get("/reverse")
def reverse(lat: float, lon: float):
    """Coordinates -> nearest street address."""
    try:
        r = httpx.get(f"{NOMINATIM}/reverse",
                      params={"lat": lat, "lon": lon, "format": "json"},
                      headers=GEO_HEADERS, timeout=8.0)
        data = r.json()
    except Exception:
        return JSONResponse(status_code=502, content={"ok": False, "error": "geocoder unavailable"})
    return {"ok": True, "display_name": data.get("display_name", "")}


@app.get("/", response_class=HTMLResponse)
def index():
    path = os.path.join(HERE, "static", "index.html")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return "<h1>UI not found</h1><p>See /docs for the API.</p>"