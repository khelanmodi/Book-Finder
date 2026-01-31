"""Search-related schemas."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SimilarTrack(BaseModel):
    """Schema for a similar track result."""

    track_id: str = Field(..., description="Track ID")
    similarity_score: float = Field(..., description="Similarity score (0-1, higher = more similar)")
    track: Dict = Field(..., description="Track metadata")


class SimilarSearchResponse(BaseModel):
    """Response schema for similarity search."""

    similar_tracks: List[SimilarTrack] = Field(
        default_factory=list,
        description="List of similar tracks sorted by similarity"
    )
    query_track: Optional[Dict] = Field(None, description="Query track info (if searching by ID)")


class UploadResponse(BaseModel):
    """Response schema for track upload."""

    uploaded_track: Dict = Field(..., description="The uploaded track metadata")
    similar_tracks: List[SimilarTrack] = Field(
        default_factory=list,
        description="Similar tracks found based on audio embedding"
    )
