import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME = "COMP3011 CW1 API"
    VERSION = "1.0.0"
    
    # Environment (dev/prod)
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "comp3011-coursework-secret-key-change-me-in-prod")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Advanced Security & Deployment
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "1") == "1"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
    GIT_SHA = os.getenv("GIT_SHA", "unknown")

settings = Settings()
