import os
from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    """
    Step 1: Define environment variables for Database connectivity (PostgreSQL).
    Step 2: Define Security settings (JWT Secret Key, Algorithm, Access Token Expire Minutes).
    Step 3: Set up CORS configurations (Allowed Origins).
    Step 4: Load settings from .env file or environment variables.
    """
    PROJECT_NAME: str = "Financial Records Management System"
    API_V1_STR: str = "/api/v1"
    
    # DB configuration placeholder
    # POSTGRES_SERVER: str
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_DB: str
    # DATABASE_URL: str
    
    # Security configuration placeholder
    # SECRET_KEY: str
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
