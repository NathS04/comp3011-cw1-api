import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
        return response

from .exceptions import NotFoundException, DuplicateException, AuthException

async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, NotFoundException):
        return JSONResponse(status_code=404, content={"detail": f"{exc.name} not found"})
    if isinstance(exc, DuplicateException):
        return JSONResponse(status_code=409, content={"detail": f"{exc.name} already exists"})
    if isinstance(exc, AuthException):
         return JSONResponse(status_code=401, content={"detail": exc.detail}, headers={"WWW-Authenticate": "Bearer"})

    # Log the full stack trace for debugging
    # In production, we might want to send this to Sentry or similar
    print(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
