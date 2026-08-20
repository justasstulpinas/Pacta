import re
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Paths whose request bodies must never appear in logs.
# Match on path prefix so UUID variants are covered.
_BODY_SUPPRESSED = re.compile(
    r"^/signing/submissions/[^/]+/(sign|verify-code|viewed|decline)$"
)


class SecureLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    - Strips request body logging for sensitive signing endpoints
    - Logs: timestamp, path, status_code, duration, IP (UUID for sensitive paths)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        path = request.url.path
        is_sensitive = bool(_BODY_SUPPRESSED.match(path))
        ip = request.client.host if request.client else "unknown"

        response = await call_next(request)

        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "path=%s status=%d ip=%s duration_ms=%d sensitive=%s",
            path,
            response.status_code,
            ip,
            duration_ms,
            is_sensitive,
        )

        return response
