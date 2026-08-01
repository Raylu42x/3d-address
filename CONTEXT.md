# CONTEXT.md

## What this project is

The **3D Word-Based Address Protocol** — an open addressing scheme that maps any
point in the near-Earth shell (≈13 km underground to 2,000 km altitude) to a
short, human-readable word address like
`installing-herd-chimera-washable-pendent-W`. The repo holds the encoding engine
(published on PyPI as `waddr`), an HTTP API that wraps it, and a web UI that
converts between street addresses, GPS coordinates, and word addresses on a map.

Addresses are stable forever: the geometry and the 27,000-word dictionary are
frozen, so every implementation and version decodes an address to the same place.

## Stack

- **Engine (`protocol/`)** — Python ≥3.9, `numpy` only. Packaged with setuptools
  via `protocol/pyproject.toml`; distribution + import name is `waddr`.
- **Backend (`backend/`)** — FastAPI + uvicorn, with `httpx`, `slowapi`,
  `pydantic` (`backend/requirements.txt`). All config comes from environment
  variables (`backend/config.py`); nothing deployment-specific is hardcoded.
- **Frontend (`frontend/`)** — static HTML/CSS/JS, no build step and no package
  manager. Served by any static server; API base is configurable at runtime.
- **Deployment** — Docker Compose plus an example Caddy reverse proxy.

## Layout

- `protocol/` — the core engine (geometry, carving, dictionary, checksum,
  encoder) and the frozen `words.txt`. No web dependencies.
- `backend/` — FastAPI service: `/v1` endpoints, validation, geocoding
  (Nominatim/Photon), rate limiting, CORS.
- `frontend/` — the web UI, favicons, manifest, robots/sitemap.
- `docker/` — `docker-compose.yml`, `Caddyfile.example`, `.env.example`.
- `docs/` — spec (`SPEC_v0.2.md`), `API.md`, `INSTALL.md`, `FEATURES.md`,
  `PUBLISHING.md`.
- `static/` — a minimal standalone page.
- `validate_wordlist.py` — dictionary validation script at the repo root.

## Commands

There is no `package.json` and no task runner; these are the real commands.

```bash
# local dev (Python, no Docker)
python3 -m venv .venv && source .venv/bin/activate
pip install ./protocol                  # the engine
pip install -r backend/requirements.txt
cd backend && uvicorn app:app --reload  # http://127.0.0.1:8000/docs

# full stack
cd docker && docker compose up -d --build

# tests — engine (run from the repo root with the package installed)
python protocol/tests/tests.py
python protocol/tests/tests_edge.py
python protocol/tests/tests_checksum.py
python protocol/tests/tests_dictionary.py
python protocol/tests/test_vectors.py   # frozen encode/decode vectors

# tests — backend API
python backend/tests/test_api.py
python -m unittest backend.tests.test_api_validation
```

No lint or build step is configured for either the Python code or the frontend.

## Things to know before changing code

- `protocol/words.txt` and the geometry are **frozen**. Changing either silently
  breaks every address ever issued; `protocol/tests/test_vectors.py` exists to
  catch that drift.
- The code is MIT, but `protocol/words.txt` and the spec are CC BY-ND 4.0 —
  modified versions may not be distributed. See `LICENSE-DICTIONARY.md`.
