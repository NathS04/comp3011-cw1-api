import time
import uuid
import logging
import hashlib
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, StreamingResponse
from .config import settings
from .rate_limit import global_limiter, auth_limiter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Generate Request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()

        # Helper to ensure headers are always applied
        def add_headers(resp: Response) -> Response:
            resp.headers["X-Request-ID"] = request_id
            resp.headers["X-Content-Type-Options"] = "nosniff"
            resp.headers["X-Frame-Options"] = "DENY"
            # Extra Security Headers
            resp.headers["Referrer-Policy"] = "no-referrer"
            resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            resp.headers["Cross-Origin-Resource-Policy"] = "same-site"

            # Default to no-store for everything (Secure by default)
            # Only if not already set (e.g. by ETag logic)
            if "Cache-Control" not in resp.headers:
                resp.headers["Cache-Control"] = "no-store"
            return resp

        # 2. Rate Limiting (Early Return)
        if settings.RATE_LIMIT_ENABLED:
            client_ip = request.client.host
            path = request.url.path
            
            limiter = auth_limiter if path.startswith("/auth/login") else global_limiter
            
            if not limiter.is_allowed(client_ip, path):
                return add_headers(JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many Requests", "request_id": request_id}
                ))

        # 3. Process Request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Catch-all for unhandled exceptions (500s)
            logger.error(f"ReqID={request_id} Unhandled Exception: {exc}", exc_info=True)
            return add_headers(JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "request_id": request_id},
            ))

        # 4. ETag & Conditional GET (Outstanding Feature)
        # Apply to successful GET requests on /events endpoints only
        if request.method == "GET" and response.status_code == 200 and request.url.path.startswith("/events"):
            # We need to capture the body to hash it.
            # CAUTION: Consuming the iterator.
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Canonical JSON hashing (if it looks like JSON)
            # But simple SHA256 of bytes is robust enough for binary text too.
            etag = f'"{hashlib.sha256(response_body).hexdigest()}"'
            
            # Check If-None-Match
            if request.headers.get("If-None-Match") == etag:
                response = Response(status_code=304) # No body for 304
                response.headers["ETag"] = etag
                response.headers["Cache-Control"] = "no-cache" # Allow caching but validate
            else:
                # Reconstruct response with body
                response = Response(
                    content=response_body,
                    status_code=200,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
                response.headers["ETag"] = etag
                response.headers["Cache-Control"] = "no-cache" # Allow caching but validate

        # 5. Logging
        process_time = time.time() - start_time
        logger.info(f"ReqID={request_id} {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
        
        return add_headers(response)

from .exceptions import NotFoundException, DuplicateException, AuthException

async def global_exception_handler(request: Request, exc: Exception):
    # Retrieve request_id if available
    request_id = getattr(request.state, "request_id", "unknown")

    # For these custom exceptions, we return simple JSON. 
    # The middleware validly wraps these if they bubble up, BUT exception handlers
    # in FastAPI run inside the middleware stack usually. 
    # However, BaseHTTPMiddleware wraps the application. 
    # Exceptions handled by FastAPI's exception_handler are returned as responses *to* the middleware.
    # So add_headers WILL apply to these.

    if isinstance(exc, NotFoundException):
        return JSONResponse(status_code=404, content={"detail": f"{exc.name} not found"})
    if isinstance(exc, DuplicateException):
        return JSONResponse(status_code=409, content={"detail": f"{exc.name} already exists"})
    if isinstance(exc, AuthException):
         return JSONResponse(status_code=401, content={"detail": exc.detail}, headers={"WWW-Authenticate": "Bearer"})

    # This catches other exceptions that might slip through (though middleware catch-all is safer).
    logger.error(f"ReqID={request_id} App Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "request_id": request_id},
    )
