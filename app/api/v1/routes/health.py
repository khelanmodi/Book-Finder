"""Health check endpoint."""
from fastapi import APIRouter
from app.core.database import db
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Health check endpoint.

    Checks:
    - MongoDB connection
    - Returns API version and status
    """
    try:
        # Ping MongoDB
        db.client.admin.command('ping')
        database_status = "connected"
        status = "healthy"
    except Exception as e:
        database_status = "disconnected"
        status = "unhealthy"

    return {
        "status": status,
        "version": settings.VERSION,
        "database": database_status
    }
