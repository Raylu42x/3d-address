# API reference

Base URL: your backend origin (e.g. `https://api.example.com`, or
`http://localhost:8000` in local development).

- All **functional** endpoints are versioned under `/v1`.
- `/health` is unversioned.
- Interactive docs (OpenAPI / Swagger UI) are served at `/docs`, and the raw
  schema at `/openapi.json`.
- CORS is enabled; allowed origins come from the `CORS_ORIGINS` env var. No
  cookies or credentials are used.
- Errors use standard HTTP status codes and a JSON body of the shape
  `{"ok": false, "error": "..."}` (protocol endpoints) — decode failures also
  include `suggestions`/`note`.

Every response includes an `"ok"` boolean.

---

## `GET /health`

Liveness plus which dictionary is loaded. Unversioned.

**Response `200`**
```json
{ "ok": true, "dictionary_source": "file", "words": 27000 }
```

---

## `POST /v1/encode`

Coordinates → address.

**Request body**

| field    | type   | default  | notes                                             |
|----------|--------|----------|---------------------------------------------------|
| `lat`    | float  | required | −90 … 90                                          |
| `lon`    | float  | required | −180 … 180                                        |
| `alt_km` | float  | `0.0`    | altitude in km; ground is `0`                     |
| `words`  | int    | `5`      | 1 … 8 (precision; more words = smaller cell)      |
| `format` | string | `words`  | `words` \| `transfer` \| `all`                    |

**Example**
```bash
curl -X POST http://localhost:8000/v1/encode \
  -H 'Content-Type: application/json' \
  -d '{"lat":51.5074,"lon":-0.1278,"alt_km":0.1,"words":5,"format":"all"}'
```

**Response `200`**
```json
{
  "ok": true,
  "indices": [4452, 12644, 6220, 4824, 5130],
  "words": "dinosaur-epidural-usable-bingo-dusty-C",
  "transfer": "C-4452-12644-6220-4824-5130",
  "lat": 51.50740025295915,
  "lon": -0.12780291125780507,
  "alt_km": 0.10003014324774995,
  "cell_edge_m": 0.5118940078290279,
  "words_used": 5
}
```
With `format: "words"` or `"transfer"`, an `"address"` field carries that single
string (the rest of the fields are still included).

**Errors**
- `422` — latitude/longitude out of range, or the point is outside the
  addressable shell (valid altitude −13 km … +2,000 km):
  `{"ok": false, "error": "point is outside the addressable shell ..."}`

---

## `POST /v1/decode`

Address → location. Auto-detects word format (`word-word-...-C`) vs transfer
format (`C-num-num-...`). Single-typo word addresses self-correct via the
checksum.

**Request body**

| field     | type   | notes                       |
|-----------|--------|-----------------------------|
| `address` | string | 1 … 200 chars               |

**Example**
```bash
curl -X POST http://localhost:8000/v1/decode \
  -H 'Content-Type: application/json' \
  -d '{"address":"dinosaur-epidural-usable-bingo-dusty-C"}'
```

**Response `200`**
```json
{
  "ok": true,
  "valid": true,
  "format": "words",
  "indices": [4452, 12644, 6220, 4824, 5130],
  "words": ["dinosaur", "epidural", "usable", "bingo", "dusty"],
  "corrections": {},
  "note": "exact",
  "lat": 51.50740025295915,
  "lon": -0.12780291125780507,
  "alt_km": 0.10003014324774995,
  "cell_edge_m": 0.5118940078290279,
  "words_used": 5
}
```
If a typo was auto-corrected, `corrections` maps the typed word to the corrected
word (e.g. `{"bingo": "bingo"}`) and `note` reflects how it resolved.

**Errors**
- `422` — could not resolve. Body includes `suggestions` (per-word candidates)
  and a `note`:
```json
{
  "ok": false, "valid": false, "format": "words",
  "suggestions": { "real": ["leal", "meal", "peal", "realm", "ream"] },
  "note": "multiple unknown words"
}
```

---

## `POST /v1/alternatives`

"That doesn't look right" — nearby checksum-valid addresses that are one
confusable word away from the supplied word address. Useful for diagnosing which
word was mistyped (early words move the address far; late words move it slightly).

**Request body:** same as `/v1/decode` (`{"address": "..."}`).

**Response `200`**
```json
{
  "ok": true,
  "alternatives": [
    {
      "words": "dinosaur-epidural-usable-bingo-duet-C",
      "changed": { "dusty": "duet" },
      "position": 4,
      "distance": 2,
      "distance_km": 0.0063,
      "lat": 51.5073874126092,
      "lon": -0.1277141239893111,
      "alt_km": 0.09985752894499456,
      "cell_edge_m": 0.5118940078290279
    }
  ]
}
```
`position` is the 0-based word that changed, `distance` the edit distance, and
`distance_km` how far the alternative lands from the supplied address's decode.
Results are sorted near-ground-first, then by smallest typo.

---

## Geocoding

These three endpoints proxy public OpenStreetMap services (Nominatim + Photon).
They are rate-limited by default (see `RATE_LIMIT_GEOCODE`) and can be disabled
entirely with `GEOCODER_ENABLED=false` — in which case they return `503`.

### `GET /v1/geocode?q=<query>`
Street address / place name → coordinates.
```json
{ "ok": true, "lat": 51.5014, "lon": -0.1419, "display_name": "Buckingham Palace, London, ..." }
```
- `404` if no match, `502` if the upstream is unavailable.

### `GET /v1/geocode_suggest?q=<partial>`
Search-as-you-type autocomplete (Photon).
```json
{ "ok": true, "results": [ { "display_name": "Big Ben, London, England", "lat": "51.50...", "lon": "-0.12..." } ] }
```

### `GET /v1/reverse?lat=<lat>&lon=<lon>`
Coordinates → nearest street address.
```json
{ "ok": true, "display_name": "10 Downing Street, London, ..." }
```

---

## Rate limiting

Limits are enforced per client IP (via `slowapi`) and are configurable by env:

| env var                | applies to                              | default      |
|------------------------|-----------------------------------------|--------------|
| `RATE_LIMIT_ENABLED`   | master switch for all limits            | `true`       |
| `RATE_LIMIT_PROTOCOL`  | `/v1/encode`, `/v1/decode`, `/v1/alternatives` | *(empty = unlimited)* |
| `RATE_LIMIT_GEOCODE`   | `/v1/geocode`, `/v1/geocode_suggest`, `/v1/reverse` | `1/second` |

Exceeding a limit returns `429 Too Many Requests`.
