# Frontend image: nginx serving the static UI.
# Build context is the REPO ROOT (see docker/docker-compose.yml).
FROM nginx:1.27-alpine

# static files (UI, config, SEO assets, social preview image, favicons, manifest)
COPY frontend/index.html frontend/about.html frontend/config.js frontend/robots.txt \
     frontend/sitemap.xml frontend/site.webmanifest frontend/og.png \
     frontend/favicon.svg frontend/favicon.ico frontend/favicon-48.png \
     frontend/apple-touch-icon.png frontend/icon-192.png frontend/icon-512.png \
     /usr/share/nginx/html/

# entrypoint hook: rewrite config.js from the API_BASE env var on container start
COPY frontend/40-render-config.sh /docker-entrypoint.d/40-render-config.sh
RUN chmod +x /docker-entrypoint.d/40-render-config.sh

EXPOSE 80
