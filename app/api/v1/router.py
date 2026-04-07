from fastapi import APIRouter
from app.api.v1.endpoints import users, records, dashboard, auth

api_router = APIRouter()

def register_v1_routes():
    """Combines all individual endpoint modules into the main v1 API router."""
    api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    api_router.include_router(users.router, prefix="/users", tags=["User Management"])
    api_router.include_router(records.router, prefix="/records", tags=["Financial Records"])
    api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Analytics"])

register_v1_routes()
