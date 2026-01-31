"""Similarity search endpoints."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import Optional
import logging

from app.api.v1.schemas.search import SimilarSearchResponse, SimilarTrack
from app.services.similarity_service import SimilarityService
from app.services.audio_service import AudioService
from app.services.track_service import TrackService
from app.utils.file_handler import FileHandler

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)


@router.post("/similar", response_model=SimilarSearchResponse)
async def search_similar(
    track_id: Optional[str] = Query(None, description="Track ID to find similar songs for"),
    file: Optional[UploadFile] = File(None, description="Audio file to find similar songs for"),
    limit: int = Query(10, le=50, description="Number of results")
):
    """
    Find similar songs by track ID or audio upload.

    Two modes:
    1. By track ID: Provide track_id parameter
    2. By audio upload: Provide file (temporary, not stored)

    Must provide exactly one of: track_id or file

    Returns top N similar tracks with similarity scores (0-1, higher = more similar)
    """
    similarity_service = SimilarityService()

    # Validate input
    if not track_id and not file:
        raise HTTPException(
            status_code=400,
            detail="Must provide either track_id or file"
        )

    if track_id and file:
        raise HTTPException(
            status_code=400,
            detail="Provide only one: track_id or file, not both"
        )

    # Mode 1: Search by track ID
    if track_id:
        try:
            track_service = TrackService()
            query_track = track_service.get_track_by_id(track_id)

            if not query_track:
                raise HTTPException(status_code=404, detail=f"Track not found: {track_id}")

            logger.info(f"Searching for tracks similar to: {query_track.get('title')}")

            similar = similarity_service.find_similar_by_track_id(track_id, limit=limit)

            return {
                "query_track": query_track,
                "similar_tracks": [SimilarTrack(**s) for s in similar]
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise HTTPException(status_code=500, detail="Search failed")

    # Mode 2: Search by uploaded audio file
    else:
        file_handler = FileHandler()
        audio_service = AudioService()
        audio_path = None

        try:
            # Validate file type
            if not file.filename.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a')):
                raise HTTPException(
                    status_code=415,
                    detail="Unsupported file type. Allowed: MP3, WAV, FLAC, OGG, M4A"
                )

            # Save to temp location
            audio_path = await file_handler.save_upload(file, temp=True)
            logger.info(f"Saved temp file: {audio_path}")

            # Process audio
            logger.info("Processing audio with librosa...")
            embedding, duration = audio_service.process_audio_file(audio_path)

            # Find similar tracks
            logger.info("Searching for similar tracks...")
            similar = similarity_service.find_similar_tracks(embedding, limit=limit)

            # Cleanup temp file
            file_handler.delete_file(audio_path)

            logger.info(f"Found {len(similar)} similar tracks")

            return {
                "query_track": None,
                "similar_tracks": [SimilarTrack(**s) for s in similar]
            }

        except Exception as e:
            # Cleanup temp file on error
            if audio_path:
                file_handler.delete_file(audio_path)
            logger.error(f"Search failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process audio: {str(e)}"
            )


@router.get("/embedding-stats")
async def get_embedding_stats():
    """
    Get statistics about embeddings in the database.

    Returns:
    - Total tracks
    - Tracks with embeddings
    - Tracks without embeddings
    - Coverage percentage
    """
    similarity_service = SimilarityService()

    try:
        stats = similarity_service.get_embedding_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get embedding stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")
