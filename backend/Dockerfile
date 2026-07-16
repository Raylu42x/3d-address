# Backend API image.
# Build context is the REPO ROOT (see docker/docker-compose.yml) so this can
# install the protocol engine from ../protocol alongside the backend code.
FROM python:3.12-slim

WORKDIR /app

# 1) install the pure protocol engine (its only dep is numpy).
#    tests are excluded from the build context via .dockerignore.
COPY protocol/ /opt/protocol/
RUN pip install --no-cache-dir /opt/protocol && rm -rf /opt/protocol

# 2) backend web dependencies (cached layer).
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) backend application code (web layer only; no protocol logic here).
COPY backend/app.py backend/config.py backend/geocoding.py backend/ratelimit.py ./

EXPOSE 8000

# --proxy-headers so client IPs (for rate limiting) survive the reverse proxy.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
