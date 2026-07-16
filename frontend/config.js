// config.js — API base URL for the frontend.
//
// In the Docker image this file is REGENERATED at container start from the
// API_BASE environment variable (see 40-render-config.sh). This checked-in
// value is only a local-development fallback. Do not hardcode a production URL
// here — set it via the API_BASE env var (containers) or the in-app Settings
// gear (per-browser runtime override).
window.API_BASE = "http://localhost:8000";
