from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
from app.db import base # Ensures all models are registered

def create_application() -> FastAPI:
    """
    Step 1: Initialize FastAPI app with title from settings.
    Step 2: Add CORSMiddleware configuration.
    Step 3: Include the main API router (/api/v1).
    Step 4: Register global exception handlers.
    Step 5: Define health-check and root endpoints.
    """
    app = FastAPI(title=settings.PROJECT_NAME)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app

app = create_application()
