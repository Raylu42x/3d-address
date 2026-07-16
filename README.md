# 3D Word-Based Address Protocol

An open addressing protocol that maps any point in the near-Earth shell
(≈8 miles underground to 2,000 km altitude) to a short, human-readable address:

```
installing-herd-chimera-washable-pendent-W        ← the Space Needle
```

Global, fully 3D, deterministic. Works the same for a front door, a drone
waypoint, or a satellite. Includes a web UI that converts between street
addresses, GPS coordinates, and word addresses on a map.

---

## Run it (container)

```bash
docker run -d -p 8000:8000 --restart unless-stopped ghcr.io/raylu42x/wordaddress:latest
```

Open `http://localhost:8000` — web UI. `http://localhost:8000/docs` — API docs.
Change the left side of `-p` to serve a different port (e.g. `-p 3000:8000`).

Or from source:

```bash
git clone https://github.com/Raylu42x/wordaddress && cd wordaddress
docker compose up -d --build
```

## Run it (Python, no Docker)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload
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

```
POST /encode           {lat, lon, alt_km, words, format} -> address + cell geometry
POST /decode           {address}                         -> location + precision
GET  /geocode?q=       street address -> coordinates      (Nominatim)
GET  /geocode_suggest  autocomplete for partial input     (Photon)
GET  /reverse?lat&lon  coordinates -> street address      (Nominatim)
GET  /health
```

Geocoding uses free public OSM services (rate-limited, ~1 req/s) — fine for
personal use; swap in a commercial geocoder for heavy traffic.

## Repository

```
geometry.py  carve.py  encoder.py     spatial core (frozen by spec)
checksum.py  dictionary.py            error detection + word layer
address.py   api.py   static/         facade, REST API, web UI
words.txt                             the official dictionary (do not modify)
tests/                                five test suites
docs/                                 specification + dictionary build brief
```

Run tests from the repo root: `python3 tests/tests.py` (same pattern for the others).

## License

Split license — see [`LICENSE`](LICENSE) and
[`LICENSE-DICTIONARY.md`](LICENSE-DICTIONARY.md):

- **Code — MIT.** Use it, change it, build on it, sell it.
- **`words.txt` + spec — CC BY-ND 4.0.** Use and redistribute freely, but
  **modified versions may not be distributed.** Every implementation must share
  the identical dictionary and geometry or addresses silently break; the frozen
  files are what make addresses interoperable. Modified forks should use a
  different protocol name to avoid confusion (see the compatibility policy in
  `LICENSE-DICTIONARY.md`).

## Status

Core, checksum, dictionary, API, and UI complete and tested. Future: `orbit.`/
`deep.` prefixes, premium alias words (surplus indices above 27,000), a
"did-you-mean" disambiguator for confusable addresses. 