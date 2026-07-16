import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ai_gateway")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        # Who is making the request?
        user = getattr(request.state, "user", None)
        identity = f"{user.username} ({user.role})" if user else "anonymous"

        logger.info(f"→ {request.method} {request.url.path} | user={identity}")

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"← {request.method} {request.url.path} "
            f"| status={response.status_code} "
            f"| {duration_ms:.1f}ms"
        )

        return response