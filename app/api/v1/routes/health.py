"""Async health check endpoint."""
from fastapi import APIRouter
from app.core.database import db
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Health check endpoint with async database ping.

    Checks:
    - Async DocumentDB connection
    - Returns API version and status
    """
    try:
        # Async ping - no blocking!
        await db.ping()
        database_status = "connected"
        status = "healthy"
    except Exception as e:
        database_status = "disconnected"
        status = "unhealthy"

    return {
        "status": status,
        "version": settings.VERSION,
        "database": database_status,
        "async": True
    }
