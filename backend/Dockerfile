# Backend API image (multi-stage).
# Build context is the REPO ROOT (see docker/docker-compose.yml) so this can
# install the waddr engine from ../protocol alongside the backend code.

# ---- builder: install waddr + backend deps into an isolated prefix ----
FROM python:3.12-slim AS builder
WORKDIR /build
# tests are excluded from the build context via .dockerignore
COPY protocol/ ./protocol/
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --prefix=/install ./protocol -r requirements.txt

# ---- runtime: copy only the installed packages, none of the build toolchain ----
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
# backend application code (web layer only; no protocol logic here)
COPY backend/app.py backend/config.py backend/geocoding.py backend/ratelimit.py ./

EXPOSE 8000

# --proxy-headers so client IPs (for rate limiting) survive the reverse proxy.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
