import os
from dotenv import load_dotenv

# Only load .env locally — never on Render (prevents stale overrides)
if not os.getenv("RENDER"):
    load_dotenv()

class Settings:
    PROJECT_NAME = "COMP3011 CW1 API"
    VERSION = "1.0.0"
    
    # Environment: Render platform always = prod (RENDER env var is set automatically)
    # Locally, respect ENVIRONMENT var or default to dev
    ENVIRONMENT = "prod" if os.getenv("RENDER") else os.getenv("ENVIRONMENT", "dev")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "comp3011-coursework-secret-key-change-me-in-prod")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Advanced Security & Deployment
    RATE_LIMIT_ENABLED = str(os.getenv("RATE_LIMIT_ENABLED", "1")).lower() in ("true", "1", "yes")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
    GIT_SHA = os.getenv("RENDER_GIT_COMMIT") or os.getenv("GIT_SHA", "unknown")

settings = Settings()
