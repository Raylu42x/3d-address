"""
ratelimit.py — shared slowapi limiter, keyed by client IP.

`limit(spec)` returns a route decorator: a real slowapi limit when `spec` is a
non-empty string, or a no-op passthrough when it is empty (meaning "unlimited").
The master `RATE_LIMIT_ENABLED` flag disables every limit at once.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

import config

# get_remote_address honors the client host; with uvicorn --proxy-headers the
# real client IP is recovered from X-Forwarded-For behind the reverse proxy.
limiter = Limiter(key_func=get_remote_address, enabled=config.RATE_LIMIT_ENABLED)


def limit(spec):
    """Decorator factory: apply `spec` if set, otherwise leave the route uncapped."""
    if not spec:
        return lambda func: func
    return limiter.limit(spec)
