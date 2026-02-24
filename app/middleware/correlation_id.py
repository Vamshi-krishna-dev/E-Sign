import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextvars import ContextVar

# Async-safe storage for the current request ID
correlation_id_ctx = ContextVar("correlation_id", default=None)

def get_correlation_id() -> str:
    """Fetch correlation ID anywhere inside the app."""
    return correlation_id_ctx.get()

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract ID from headers or generate a new one
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set into context for async operations
        correlation_id_ctx.set(req_id)

        # Process request
        response: Response = await call_next(request)

        # Always return request ID in response headers
        response.headers["X-Request-ID"] = req_id
        return response