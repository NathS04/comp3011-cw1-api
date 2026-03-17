import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .api.admin import router as admin_router
from .api.analytics import router as analytics_router
from .api.routes import router as api_router
from .core.config import settings
from .core.middleware import RequestLoggingMiddleware, global_exception_handler

logger = logging.getLogger(__name__)

app = FastAPI(
    title="COMP3011 CW1 API",
    description="Event RSVP Management API for coursework 1.",
    version="1.0.0",
    contact={
        "name": "Nathaniel Sebastian",
        "email": "sc232ns@leeds.ac.uk",
    },
)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Application starting up...")


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


origins: list[str] = ["*"]
allow_credentials = False

if settings.ALLOWED_ORIGINS:
    origins = settings.ALLOWED_ORIGINS.split(",")
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(analytics_router)
app.include_router(api_router)
app.include_router(admin_router)
