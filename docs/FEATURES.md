# Product features and app flow

This document summarizes the current user experience and the main moving parts of the project.

## 1. What the app does

The project is a full-stack 3D address system that converts between:

- street addresses
- GPS coordinates
- word-based addresses

A single conversion flow updates all three views so the user can move between formats without re-entering data.

## 2. Web UI capabilities

The frontend in [frontend/index.html](../frontend/index.html) provides a polished experience for everyday use:

- convert from any one input to the other two
- show the address on a Leaflet map
- display precision information for the chosen word length
- explain visible corrections when a typo is auto-corrected
- show altitude context with ground elevation and final height
- generate shareable URLs that preserve the current address
- copy words, GPS coordinates, or share links with one click
- open a QR-share modal for the current location link
- keep a short recent-address history in browser storage
- switch between official, local, or custom API backends from the gear icon

These features are designed to make the app feel more like a practical product than a prototype.

## 3. Backend capabilities

The backend in [backend/app.py](../backend/app.py) exposes the protocol over HTTP:

- encode a coordinate to a word address
- decode a word address back to coordinates
- return nearby alternatives for confusing or mistyped inputs
- geocode street addresses and reverse-geocode coordinates
- enforce input validation and rate limiting

The protocol logic itself lives in [protocol/](../protocol), while the backend is intentionally thin and focuses on HTTP, validation, geocoding, and CORS.

## 4. Repository organization

- [protocol/](../protocol) — the core engine, dictionary, geometry, and address logic
- [backend/](../backend) — FastAPI service and API routing
- [frontend/](../frontend) — static web UI and assets
- [docker/](../docker) — deployment and reverse-proxy configuration
- [docs/](../docs) — product docs, API reference, install guide, and protocol notes

## 5. Typical local workflow

1. Install the protocol engine locally.
2. Start the backend with Uvicorn.
3. Serve the frontend from a static web server.
4. Open the UI and convert an address.

For the quickest local setup, see [docs/INSTALL.md](INSTALL.md).

## 6. Deployment notes

The project is intended to run in two parts:

- a backend API service
- a frontend static site

In production, the frontend should point at a real API origin through the configured API base URL or the runtime settings UI.
