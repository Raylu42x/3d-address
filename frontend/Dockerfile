# Frontend image: nginx serving the static UI.
# Build context is the REPO ROOT (see docker/docker-compose.yml).
FROM nginx:1.27-alpine

# static files (UI, config, SEO assets, social preview image)
COPY frontend/index.html frontend/config.js frontend/favicon.svg \
     frontend/og.png frontend/robots.txt frontend/sitemap.xml \
     /usr/share/nginx/html/

# entrypoint hook: rewrite config.js from the API_BASE env var on container start
COPY frontend/40-render-config.sh /docker-entrypoint.d/40-render-config.sh
RUN chmod +x /docker-entrypoint.d/40-render-config.sh

EXPOSE 80
