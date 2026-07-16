# Frontend image: nginx serving the static UI.
# Build context is the REPO ROOT (see docker/docker-compose.yml).
FROM nginx:1.27-alpine

# static files
COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/config.js  /usr/share/nginx/html/config.js

# entrypoint hook: rewrite config.js from the API_BASE env var on container start
COPY frontend/40-render-config.sh /docker-entrypoint.d/40-render-config.sh
RUN chmod +x /docker-entrypoint.d/40-render-config.sh

EXPOSE 80
