#!/bin/sh
# Runs on nginx container start (via /docker-entrypoint.d). Regenerates config.js
# from the API_BASE env var so the frontend points at the right backend without
# baking a URL into the image. Empty API_BASE -> same-origin requests.
set -e
ROOT=/usr/share/nginx/html

# 1) config.js — the API base URL the browser calls
: "${API_BASE:=}"
cat > "$ROOT/config.js" <<EOF
// generated at container start from the API_BASE env var
window.API_BASE = "${API_BASE}";
EOF
echo "config.js: window.API_BASE = \"${API_BASE}\""

# 2) SEO absolute URLs — substitute the __SITE_URL__ placeholder in the static
#    files from the SITE_URL env var (needed for canonical / OG / sitemap, which
#    social crawlers read from the raw HTML and require absolute URLs).
: "${SITE_URL:=}"
SITE_URL="${SITE_URL%/}"   # strip any trailing slash
for f in index.html robots.txt sitemap.xml; do
  [ -f "$ROOT/$f" ] && sed -i "s|__SITE_URL__|${SITE_URL}|g" "$ROOT/$f"
done
echo "SEO: SITE_URL = \"${SITE_URL}\""
