import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ── Config ────────────────────────────────────────────────────────────────────

# Stricter limits on auth routes to block brute force
RATE_LIMIT_RULES = {
    "/auth/login":    {"max_requests": 5,   "window_seconds": 60},
    "/auth/register": {"max_requests": 10,  "window_seconds": 60},
    "default":        {"max_requests": 100, "window_seconds": 60},
}


# ── In-memory store ───────────────────────────────────────────────────────────
# Structure: { "ip:path": [(timestamp), ...] }

request_log: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path

        rule = RATE_LIMIT_RULES.get(path, RATE_LIMIT_RULES["default"])
        max_requests = rule["max_requests"]
        window = rule["window_seconds"]

        key = f"{client_ip}:{path}"
        now = time.time()

        # Drop timestamps outside the current window
        request_log[key] = [
            t for t in request_log[key] if now - t < window
        ]

        if len(request_log[key]) >= max_requests:
            retry_after = int(window - (now - request_log[key][0]))
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Too many requests. Retry after {retry_after}s."
                },
                headers={"Retry-After": str(retry_after)},
            )

        request_log[key].append(now)
        return await call_next(request)