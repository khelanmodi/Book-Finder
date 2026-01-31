"""Statistics endpoints."""
from fastapi import APIRouter, HTTPException
import logging

from app.api.v1.schemas.stats import TopArtistsResponse, MoodDistribution, ListeningStats
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["statistics"])
logger = logging.getLogger(__name__)


@router.get("/top-artists", response_model=TopArtistsResponse)
async def get_top_artists(limit: int = 5):
    """
    Get top artists for the current month.

    - Aggregates by artist
    - Counts plays in current month
    - Returns artist name, play count, and sample tracks
    - Default limit: 5
    """
    stats_service = StatsService()

    try:
        result = stats_service.get_top_artists_this_month(limit=limit)
        return result
    except Exception as e:
        logger.error(f"Failed to get top artists: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@router.get("/mood-distribution", response_model=list[MoodDistribution])
async def get_mood_distribution():
    """
    Get distribution of moods across all tracks.

    Returns count and percentage for each mood.
    """
    stats_service = StatsService()

    try:
        result = stats_service.get_mood_distribution()
        return result
    except Exception as e:
        logger.error(f"Failed to get mood distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@router.get("/listening", response_model=ListeningStats)
async def get_listening_stats():
    """
    Get overall listening statistics.

    Returns:
    - Total tracks
    - Unique artists and albums
    - Total duration and average duration
    """
    stats_service = StatsService()

    try:
        result = stats_service.get_listening_stats()
        return result
    except Exception as e:
        logger.error(f"Failed to get listening stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")
