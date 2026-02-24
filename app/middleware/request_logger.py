import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger
from app.middleware.correlation_id import get_correlation_id


class RequestLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start = time.time()

        correlation_id = get_correlation_id()

        # Extract client IP
        client_ip = (
            request.headers.get("x-forwarded-for")
            or request.client.host
            or "unknown"
        )

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # Ensure logging works even when endpoint crashes
            duration = round(time.time() - start, 3)
            logger.error(
                f"REQUEST_FAILED | CID={correlation_id} | "
                f"{request.method} {request.url.path} | "
                f"IP={client_ip} | "
                f"Error={exc} | Duration={duration}s",
                exc_info=True
            )
            raise

        duration = round(time.time() - start, 3)

        # Extract response size safely
        resp_size = (
            response.headers.get("content-length", "unknown")
        )

        logger.info(
            f"REQUEST_LOG | CID={correlation_id} | "
            f"{request.method} {request.url.path} | "
            f"Status={response.status_code} | "
            f"IP={client_ip} | "
            f"Size={resp_size} | "
            f"Duration={duration}s"
        )

        # Slow API detection (>2s)
        if duration > 2.0:
            logger.warning(
                f"SLOW_API | CID={correlation_id} | "
                f"{request.method} {request.url.path} took {duration}s"
            )

        return response