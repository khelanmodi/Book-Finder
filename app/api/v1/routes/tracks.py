"""Track management endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.api.v1.schemas.track import TrackCreate, TrackResponse, TrackUpdate
from app.services.track_service import TrackService
from app.services.mood_service import MoodService

router = APIRouter(prefix="/tracks", tags=["tracks"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=TrackResponse, status_code=201)
async def create_track(track_data: TrackCreate):
    """
    Log a new track.

    - If mood is not provided, it will be inferred from tags
    - playedAt defaults to current time if not provided
    - Returns the created track with inferred mood
    """
    track_service = TrackService()
    mood_service = MoodService()

    # Convert Pydantic model to dict
    track_dict = track_data.model_dump()

    # Infer mood if not provided
    if not track_dict.get('mood') and track_dict.get('tags'):
        inferred_mood = mood_service.infer_mood(track_dict['tags'])
        if inferred_mood:
            track_dict['mood'] = inferred_mood
            logger.info(f"Inferred mood '{inferred_mood}' from tags: {track_dict['tags']}")

    # Set playedAt to now if not provided
    if not track_dict.get('playedAt'):
        track_dict['playedAt'] = datetime.utcnow()

    try:
        created_track = track_service.create_track(track_dict)
        logger.info(
            f"Logged track: {created_track['title']} – {created_track['artist']} "
            f"(mood: {created_track.get('mood')}, source: {created_track.get('source')})"
        )
        return created_track
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create track: {e}")
        raise HTTPException(status_code=500, detail="Failed to create track")


@router.get("/", response_model=List[TrackResponse])
async def get_tracks(
    mood: Optional[str] = Query(None, description="Filter by mood"),
    artist: Optional[str] = Query(None, description="Filter by artist (case-insensitive)"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get tracks with optional filtering.

    - Filter by mood: GET /tracks?mood=focus
    - Filter by artist: GET /tracks?artist=Daft Punk
    - Pagination: use limit and skip parameters
    - Results are sorted by playedAt (most recent first)
    """
    track_service = TrackService()

    try:
        tracks = track_service.get_tracks(
            mood=mood,
            artist=artist,
            limit=limit,
            skip=skip
        )
        return tracks
    except Exception as e:
        logger.error(f"Failed to fetch tracks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tracks")


@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(track_id: str):
    """Get a specific track by ID."""
    track_service = TrackService()

    track = track_service.get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Track not found: {track_id}")

    return track


@router.patch("/{track_id}", response_model=TrackResponse)
async def update_track(track_id: str, update_data: TrackUpdate):
    """Update a track."""
    track_service = TrackService()

    # Convert Pydantic model to dict, excluding unset fields
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_track = track_service.update_track(track_id, update_dict)
    if not updated_track:
        raise HTTPException(status_code=404, detail=f"Track not found: {track_id}")

    logger.info(f"Updated track: {track_id}")
    return updated_track


@router.delete("/{track_id}", status_code=204)
async def delete_track(track_id: str):
    """Delete a track."""
    track_service = TrackService()

    deleted = track_service.delete_track(track_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Track not found: {track_id}")

    logger.info(f"Deleted track: {track_id}")
    return None
