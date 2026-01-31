"""Statistics-related schemas."""
from typing import List
from pydantic import BaseModel, Field


class ArtistStat(BaseModel):
    """Schema for artist statistics."""

    artist: str = Field(..., description="Artist name")
    play_count: int = Field(..., description="Number of times played")
    sample_tracks: List[str] = Field(default_factory=list, description="Sample track titles")


class TopArtistsResponse(BaseModel):
    """Response schema for top artists."""

    range: dict = Field(..., description="Date range for statistics")
    topArtists: List[ArtistStat] = Field(default_factory=list, description="Top artists by play count")


class MoodDistribution(BaseModel):
    """Schema for mood distribution."""

    mood: str
    count: int
    percentage: float


class ListeningStats(BaseModel):
    """Schema for overall listening statistics."""

    total_tracks: int
    unique_artists: int
    unique_albums: int
    total_duration_seconds: float
    average_duration_seconds: float
    total_duration_hours: float
