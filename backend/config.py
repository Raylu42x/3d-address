"""
config.py — all backend configuration comes from environment variables.

Nothing deployment-specific is hardcoded here: domains, CORS origins, rate
limits, and the upstream geocoder URLs are all overridable via env. Defaults are
chosen so `uvicorn app:app` runs out of the box for local development.
"""
import os


def _str(name, default):
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


def _bool(name, default):
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _list(name, default):
    """Comma-separated env var -> list of trimmed values (default if unset)."""
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return [item.strip() for item in v.split(",") if item.strip()]


# --- CORS ---
# CORS_ORIGINS is a comma-separated allowlist. If unset, default to "*"
# (open) — self-hosters should set it to their frontend origin(s) in prod.
# No cookies/credentials are ever used, so "*" is safe for a public API.
CORS_ORIGINS = _list("CORS_ORIGINS", ["*"])

# --- rate limiting (slowapi) ---
# Master switch: self-hosters can disable all limits with RATE_LIMIT_ENABLED=false.
RATE_LIMIT_ENABLED = _bool("RATE_LIMIT_ENABLED", True)

# Protocol endpoints are cheap and stateless -> generous / unlimited by default.
# An empty value means "no limit". Format is slowapi syntax, e.g. "120/minute".
RATE_LIMIT_PROTOCOL = _str("RATE_LIMIT_PROTOCOL", "")

# Geocoding endpoints proxy public OSM services (Nominatim/Photon) that publish
# strict usage policies (~1 req/s). Keep these limited by default.
RATE_LIMIT_GEOCODE = _str("RATE_LIMIT_GEOCODE", "1/second")

# --- geocoding upstreams ---
# Feature flag so a deployment can turn geocoding off entirely (protocol-only).
GEOCODER_ENABLED = _bool("GEOCODER_ENABLED", True)

# Upstream service base URLs (overridable so operators can swap in their own
# hosted geocoders instead of the shared public instances).
NOMINATIM_URL = _str("NOMINATIM_URL", "https://nominatim.openstreetmap.org")
PHOTON_URL = _str("PHOTON_URL", "https://photon.komoot.io")

# Nominatim's policy requires an identifying User-Agent.
GEO_USER_AGENT = _str("GEO_USER_AGENT", "WordAddressProtocol/0.2 (self-hosted)")

# Upstream request timeout (seconds).
GEO_TIMEOUT = float(_str("GEO_TIMEOUT", "8"))
