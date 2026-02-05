from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .api.analytics import router as analytics_router
from .core.middleware import RequestLoggingMiddleware, global_exception_handler

app = FastAPI(
    title="COMP3011 CW1 API",
    description="Event RSVP Management API for coursework 1.",
    version="1.0.0",
    contact={
        "name": "Nathaniel Sebastian",
        "email": "sc232ns@leeds.ac.uk",
    },
)

import logging
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# CORS
from .core.config import settings

# CORS Logic
origins = ["*"]
allow_credentials = False

# In production (if allowed origins are set), restrict it
if settings.ALLOWED_ORIGINS:
    origins = settings.ALLOWED_ORIGINS.split(",")
    allow_credentials = True  # Strict origins + credentials allowed

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Custom Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(analytics_router)
app.include_router(api_router)

from .api.admin import router as admin_router
app.include_router(admin_router)
