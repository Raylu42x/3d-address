"""
app.py — REST service for the 3D word-address protocol.

This is the web layer only. All protocol logic lives in the installed `protocol`
package; nothing here reimplements encoding, decoding, or the dictionary.

Run (from this directory, with the protocol package installed):
    pip install ../protocol
    uvicorn app:app --reload
    open http://127.0.0.1:8000/docs   (interactive API docs)

Functional endpoints are versioned under /v1; /health is unversioned.
CORS origins, rate limits, and geocoder settings all come from env (see config.py).
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from waddr import encode_all, decode as protocol_decode, alternatives as protocol_alternatives
from waddr import dictionary as D

import config
import geocoding
from ratelimit import limiter, limit

app = FastAPI(title="3D Word-Based Address Protocol", version="0.2")

# --- rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS (no credentials; origins from CORS_ORIGINS env) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class EncodeReq(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    alt_km: float = Field(0.0, ge=-13000, le=2000000)
    words: int = Field(5, ge=1, le=8)
    format: str = Field("words", max_length=16)  # "words" | "transfer" | "all"


class DecodeReq(BaseModel):
    address: str = Field(..., min_length=1, max_length=200)


@app.get("/health")
def health():
    return {"ok": True, "dictionary_source": D.SOURCE, "words": len(D.WORD_LIST)}


@app.post("/v1/encode")
@limit(config.RATE_LIMIT_PROTOCOL)
def encode(request: Request, r: EncodeReq):
    try:
        full = encode_all(r.lat, r.lon, r.alt_km, r.words)
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


@app.post("/v1/decode")
@limit(config.RATE_LIMIT_PROTOCOL)
def decode(request: Request, r: DecodeReq):
    res = protocol_decode(r.address)
    status = 200 if res.get("valid") else 422
    return JSONResponse(status_code=status, content={"ok": res.get("valid", False), **res})


@app.post("/v1/alternatives")
@limit(config.RATE_LIMIT_PROTOCOL)
def alternatives(request: Request, r: DecodeReq):
    """'That doesn't look right' — nearby valid addresses one confusable word away."""
    return {"ok": True, "alternatives": protocol_alternatives(r.address)}


# geocoding endpoints (/v1/geocode, /v1/reverse, /v1/geocode_suggest)
app.include_router(geocoding.router, prefix="/v1")
