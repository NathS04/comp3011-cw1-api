from fastapi import FastAPI
from .api.routes import router

app = FastAPI(title="COMP3011 CW1 API", version="0.1.0")
app.include_router(router)
