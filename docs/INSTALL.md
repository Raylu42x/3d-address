# Self-hosting guide

The app is two containers — a **backend** (FastAPI API) and a **frontend**
(nginx serving the static UI) — plus a host-level **Caddy** reverse proxy that
terminates TLS. The compose services bind only to `127.0.0.1`, so nothing is
exposed to the internet except through Caddy.

```
browser ──▶ Caddy (host, :443)
              ├─ FRONTEND_DOMAIN ─▶ 127.0.0.1:8080  (frontend nginx)
              └─ API_DOMAIN      ─▶ 127.0.0.1:8000  (backend uvicorn)
```

## Prerequisites

- Docker + Docker Compose
- A host with two DNS records pointing at it (one for the UI, one for the API)
- [Caddy](https://caddyserver.com/) installed on the host (for automatic HTTPS)

## 1. Configure

```bash
git clone https://github.com/Raylu42x/wordaddress && cd wordaddress
cp docker/.env.example docker/.env
```

Edit `docker/.env`:

| variable            | what it does                                                        |
|---------------------|--------------------------------------------------------------------|
| `FRONTEND_DOMAIN`   | public domain for the UI (used by Caddy)                           |
| `API_DOMAIN`        | public domain for the API (used by Caddy)                         |
| `API_BASE`          | API origin the browser calls — set to `https://<API_DOMAIN>`      |
| `CORS_ORIGINS`      | allowlist of origins allowed to call the API — set to `https://<FRONTEND_DOMAIN>` |
| `RATE_LIMIT_*`      | rate limits (see below)                                            |
| `GEOCODER_ENABLED`  | `true`/`false` — turn the OSM geocoding proxies on/off             |

`API_BASE` and `CORS_ORIGINS` **must** be set to your real domains in
production, or the browser can't reach the API / CORS will block it.

## 2. Bring up the containers

```bash
cd docker
docker compose up -d --build
```

Check them:
```bash
curl http://127.0.0.1:8000/health          # backend
curl -I http://127.0.0.1:8080/             # frontend
```

## 3. Reverse proxy (Caddy on the host)

```bash
cp docker/Caddyfile.example /etc/caddy/Caddyfile   # or wherever your Caddy reads from
export FRONTEND_DOMAIN=address.example.com
export API_DOMAIN=api.example.com
sudo systemctl reload caddy
```

The example `Caddyfile` reads `{$FRONTEND_DOMAIN}` and `{$API_DOMAIN}` from the
environment and proxies them to the two local ports. Caddy provisions HTTPS
certificates automatically. If you run Caddy under systemd, set the two
variables in the unit (e.g. an `Environment=` line or a drop-in) rather than a
shell export.

Visit `https://<FRONTEND_DOMAIN>` — the UI loads and talks to
`https://<API_DOMAIN>/v1/...`.

## Rate limiting

Limits are keyed by client IP (`slowapi`). Because the backend runs behind a
proxy, it starts uvicorn with `--proxy-headers` so the real client IP is
recovered from `X-Forwarded-For`.

- `RATE_LIMIT_ENABLED=false` disables **all** limits (handy for a private
  instance).
- `RATE_LIMIT_PROTOCOL` limits the cheap protocol endpoints (empty = unlimited).
- `RATE_LIMIT_GEOCODE` limits the geocoding endpoints, which proxy public OSM
  services with their own usage policies (default `1/second`).

## Running without Docker (development)

```bash
# 1) install the protocol engine
pip install ./protocol

# 2) run the API
pip install -r backend/requirements.txt
cd backend && uvicorn app:app --reload      # http://127.0.0.1:8000/docs

# 3) serve the frontend (any static server); it defaults to http://localhost:8000
cd frontend && python3 -m http.server 8080  # http://localhost:8080
```

The UI's gear icon (top-right) lets you point the frontend at a different API
server at runtime — **Official**, **Local** (`http://localhost:8000`), or a
**Custom URL** — persisted in your browser's `localStorage`.

## Updating

```bash
git pull
cd docker && docker compose up -d --build
```

Addresses are stable across versions by design — the protocol geometry and
dictionary are frozen, so an address encoded by any version decodes to the same
place in every other version.
