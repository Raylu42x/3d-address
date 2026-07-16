#!/bin/sh
# Runs on nginx container start (via /docker-entrypoint.d). Regenerates config.js
# from the API_BASE env var so the frontend points at the right backend without
# baking a URL into the image. Empty API_BASE -> same-origin requests.
set -e
: "${API_BASE:=}"
cat > /usr/share/nginx/html/config.js <<EOF
// generated at container start from the API_BASE env var
window.API_BASE = "${API_BASE}";
EOF
echo "config.js: window.API_BASE = \"${API_BASE}\""
