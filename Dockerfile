# 3D Word-Based Address Protocol — API + web UI
FROM python:3.12-slim

WORKDIR /app

# install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app source
COPY geometry.py carve.py encoder.py checksum.py dictionary.py address.py api.py ./
COPY static/ ./static/
# the dictionary; falls back to a placeholder list if absent
COPY words.txt* ./

EXPOSE 8000

# --proxy-headers so it behaves behind a reverse proxy (nginx/caddy) on the VPS
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]