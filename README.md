# 3D Word-Based Address Protocol

[![PyPI](https://img.shields.io/pypi/v/waddr.svg)](https://pypi.org/project/waddr/)
**Try it live:** [address.kervian.com](https://address.kervian.com) · `pip install waddr`

An open addressing protocol that maps any point in the near-Earth shell
(≈13 km underground to 2,000 km altitude) to a short, human-readable address:

```
installing-herd-chimera-washable-pendent-W        ← the Space Needle
```

Global, fully 3D, deterministic. Works the same for a front door, a drone
waypoint, or a satellite. Includes a web UI that converts between street
addresses, GPS coordinates, and word addresses on a map.

Addresses are **stable forever**: the geometry and dictionary are frozen, so a
valid address decodes to the same place in every implementation and every
version.

---

## Repository layout

```
protocol/    the pure engine — the actual product. No web deps (numpy only).
             pip-installable ("waddr"); ships the official words.txt dictionary.
backend/     FastAPI service that imports the protocol package. Geocoding,
             CORS, and rate limiting. Serves the API only (versioned under /v1).
frontend/    the static web UI (index.html) + nginx image. Talks to the backend
             via a configurable API base URL.
docker/      docker-compose + host Caddy reverse-proxy example + .env.example.
docs/        the spec, API reference, install guide, and dictionary brief.
```

## Quick start (Docker)

```bash
git clone https://github.com/Raylu42x/3d-address && cd 3d-address
cp docker/.env.example docker/.env      # edit domains / API_BASE / CORS
cd docker && docker compose up -d --build
```

Backend on `127.0.0.1:8000`, frontend on `127.0.0.1:8080`. Put a reverse proxy
(see [`docker/Caddyfile.example`](docker/Caddyfile.example)) in front for public
HTTPS. Full walkthrough: [`docs/INSTALL.md`](docs/INSTALL.md).

## Quick start (Python, no Docker)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install ./protocol                  # the engine
pip install -r backend/requirements.txt
cd backend && uvicorn app:app --reload  # http://127.0.0.1:8000/docs
```

Serve `frontend/` with any static server; it defaults to `http://localhost:8000`
and can be pointed elsewhere via the in-app Settings gear.

## Use the engine directly

The engine is published on PyPI as [**`waddr`**](https://pypi.org/project/waddr/) —
no web dependencies, just numpy:

```bash
pip install waddr
```

```python
from waddr import encode_all, decode

info = encode_all(51.5074, -0.1278, alt_km=0.1, words=5)
print(info["words"])                 # dinosaur-epidural-usable-bingo-dusty-C
print(decode(info["words"])["lat"])  # 51.5074...
```

---

## How an address works

`word-word-word-word-word-C` — each word narrows the location ~27,000×; the
final letter is a checksum that catches typos (which the decoder auto-corrects
when possible). Machines can skip the words entirely and exchange the numeric
transfer form `C-4452-12644-6220-4824-5130`.

| Words | Cell size | Good for               |
|-------|-----------|------------------------|
| 3     | ~460 m    | Neighborhood / block   |
| 4     | ~15 m     | Property / single home |
| 5     | ~51 cm    | Doorway (human standard) |
| 6     | ~1.7 cm   | Hand / device          |
| 7     | ~0.6 mm   | Robotics / engineering |

A hollow spherical shell (Earth −13 km to +2,000 km) is carved out of a
17,000 km cube: a 41³ level-1 grid (25,460 valid cells), then 30³ recursive
subdivision per added word — hence the 27,000-word dictionary. Full detail:
[`docs/SPEC_v0.2.md`](docs/SPEC_v0.2.md).

## API

Functional endpoints are versioned under `/v1`; `/health` is unversioned;
interactive docs live at `/docs`.

```
POST /v1/encode          {lat, lon, alt_km, words, format} -> address + geometry
POST /v1/decode          {address}                         -> location + precision
POST /v1/alternatives    {address}                         -> nearby valid addresses
GET  /v1/geocode?q=      street address -> coordinates      (Nominatim)
GET  /v1/geocode_suggest autocomplete for partial input     (Photon)
GET  /v1/reverse?lat&lon coordinates -> street address      (Nominatim)
GET  /health
```

Full request/response examples: [`docs/API.md`](docs/API.md).

Geocoding uses free public OSM services (rate-limited by default) — fine for
personal use; point `NOMINATIM_URL`/`PHOTON_URL` at your own instance, or set
`GEOCODER_ENABLED=false`, for heavy traffic.

## Self-hosting

Anyone can run their own instance — and because the dictionary and geometry are
frozen, a self-hosted copy produces the **exact same addresses** as every other
instance. It's another node of one protocol, not a fork. Three levels:

1. **Just the library** — `pip install waddr`, `from waddr import encode_all, decode`.
   No server needed. This is most developers.
2. **The API only** — run `backend/` (`pip install ./protocol -r backend/requirements.txt`
   then `uvicorn app:app`), or the backend container. Gives you the `/v1` endpoints.
3. **The full web app** — backend + frontend + HTTPS via Docker. Point four env
   values at your own domains (`FRONTEND_DOMAIN`, `API_DOMAIN`, `API_BASE`,
   `CORS_ORIGINS`) and `docker compose up -d --build`.

Full walkthrough — including the Caddy reverse-proxy config for automatic
HTTPS — is in [`docs/INSTALL.md`](docs/INSTALL.md). Publishing the package
yourself: [`docs/PUBLISHING.md`](docs/PUBLISHING.md).

## Tests

Tests live next to what they cover and are excluded from the Docker images.

```bash
# protocol engine (run with the package installed, from the repo root)
python protocol/tests/tests.py
python protocol/tests/tests_edge.py
python protocol/tests/tests_checksum.py
python protocol/tests/tests_dictionary.py
python protocol/tests/test_vectors.py     # frozen encode/decode vectors

# backend API
python backend/tests/test_api.py
python -m unittest backend.tests.test_api_validation
```

`protocol/tests/vectors.json` pins `(lat, lon, alt, words) -> address` for a
diverse set of points; `test_vectors.py` fails if encoder output ever drifts —
the guardrail that keeps addresses decodable forever.

## License

Split license — see [`LICENSE`](LICENSE) and
[`LICENSE-DICTIONARY.md`](LICENSE-DICTIONARY.md):

- **Code — MIT.** Use it, change it, build on it, sell it.
- **`protocol/words.txt` + spec — CC BY-ND 4.0.** Use and redistribute freely,
  but **modified versions may not be distributed.** Every implementation must
  share the identical dictionary and geometry or addresses silently break; the
  frozen files are what make addresses interoperable. Modified forks should use
  a different protocol name to avoid confusion (see the compatibility policy in
  `LICENSE-DICTIONARY.md`).

## Status

Core, checksum, dictionary, API, and UI complete and tested. Future: `orbit.`/
`deep.` prefixes, premium alias words (surplus indices above 27,000), a
"did-you-mean" disambiguator for confusable addresses.
