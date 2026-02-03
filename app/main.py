from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(router)
