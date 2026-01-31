"""Track-related schemas for request/response validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TrackCreate(BaseModel):
    """Request schema for creating a track."""

    title: str = Field(..., min_length=1, max_length=200, description="Track title")
    artist: str = Field(..., min_length=1, max_length=200, description="Artist name")
    album: Optional[str] = Field(None, max_length=200, description="Album name")
    mood: Optional[str] = Field(None, description="Mood: focus, energetic, chill, melancholic, happy")
    playedAt: Optional[datetime] = Field(None, description="When track was played (defaults to now)")
    source: str = Field(default="manual", max_length=50, description="Source: manual, upload, spotify, youtube")
    tags: List[str] = Field(default_factory=list, description="Tags for mood inference")

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, v):
        """Validate mood is one of the allowed values."""
        if v is not None:
            allowed_moods = ['focus', 'energetic', 'chill', 'melancholic', 'happy']
            if v not in allowed_moods:
                raise ValueError(f'Mood must be one of: {", ".join(allowed_moods)}')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Ensure tags are non-empty strings."""
        return [tag.strip() for tag in v if tag.strip()]


class TrackResponse(BaseModel):
    """Response schema for track queries."""

    id: str = Field(alias="_id", description="Track ID")
    title: str
    artist: str
    album: Optional[str] = None
    mood: Optional[str] = None
    playedAt: datetime
    source: str
    tags: List[str] = Field(default_factory=list)
    audioPath: Optional[str] = None
    duration: Optional[float] = Field(None, description="Duration in seconds")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TrackUpdate(BaseModel):
    """Request schema for updating a track."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    artist: Optional[str] = Field(None, min_length=1, max_length=200)
    album: Optional[str] = Field(None, max_length=200)
    mood: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, v):
        """Validate mood is one of the allowed values."""
        if v is not None:
            allowed_moods = ['focus', 'energetic', 'chill', 'melancholic', 'happy']
            if v not in allowed_moods:
                raise ValueError(f'Mood must be one of: {", ".join(allowed_moods)}')
        return v
