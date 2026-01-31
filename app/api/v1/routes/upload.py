"""File upload endpoint for MP3 files."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import logging

from app.api.v1.schemas.search import UploadResponse, SimilarTrack
from app.services.audio_service import AudioService
from app.services.track_service import TrackService
from app.services.similarity_service import SimilarityService
from app.services.mood_service import MoodService
from app.utils.file_handler import FileHandler

router = APIRouter(prefix="/tracks/upload", tags=["upload"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=UploadResponse)
async def upload_track(
    file: UploadFile = File(..., description="MP3 audio file"),
    title: Optional[str] = Form(None, description="Track title"),
    artist: Optional[str] = Form(None, description="Artist name"),
    album: Optional[str] = Form(None, description="Album name"),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
    mood: Optional[str] = Form(None, description="Mood (or auto-infer from tags)")
):
    """
    Upload an MP3 file and get similar songs.

    Steps:
    1. Validate and save the MP3 file
    2. Extract audio features using librosa
    3. Create 128-dim embedding vector
    4. Save track to database with metadata
    5. Find top 10 similar tracks
    6. Return uploaded track + similar tracks

    Max file size: 10MB
    Supported formats: MP3, WAV, FLAC, OGG, M4A
    """
    file_handler = FileHandler()
    audio_service = AudioService()
    track_service = TrackService()
    similarity_service = SimilarityService()
    mood_service = MoodService()

    # Validate file type
    if not file.filename.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a')):
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Allowed: MP3, WAV, FLAC, OGG, M4A"
        )

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum: 10MB"
        )

    audio_path = None
    try:
        # Save file permanently
        audio_path = await file_handler.save_upload(file, temp=False)
        logger.info(f"Saved uploaded file: {audio_path} ({file_size} bytes)")

        # Process audio: extract features and create embedding
        logger.info("Processing audio with librosa...")
        embedding, duration = audio_service.process_audio_file(audio_path)

        # Parse tags
        tag_list = [t.strip() for t in tags.split(',')] if tags else []

        # Infer mood if not provided
        if not mood and tag_list:
            mood = mood_service.infer_mood(tag_list)
            logger.info(f"Inferred mood: {mood} from tags: {tag_list}")

        # Create track record
        track_data = {
            "title": title or file.filename.replace('.mp3', '').replace('.wav', ''),
            "artist": artist or "Unknown",
            "album": album,
            "mood": mood,
            "tags": tag_list,
            "source": "upload",
            "audioPath": audio_path,
            "embedding": embedding.tolist(),
            "duration": duration
        }

        created_track = track_service.create_track(track_data)
        logger.info(f"Created track: {created_track['_id']}")

        # Find similar tracks
        logger.info("Searching for similar tracks...")
        similar = similarity_service.find_similar_tracks(
            embedding,
            limit=10,
            exclude_track_id=created_track['_id']
        )

        logger.info(f"Found {len(similar)} similar tracks")

        return {
            "uploaded_track": created_track,
            "similar_tracks": [SimilarTrack(**s) for s in similar]
        }

    except Exception as e:
        # Cleanup file on error
        if audio_path:
            file_handler.delete_file(audio_path)
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audio: {str(e)}"
        )
