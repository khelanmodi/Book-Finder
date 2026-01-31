"""Track data model."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Track(BaseModel):
    """Track document model matching MongoDB schema."""

    id: Optional[str] = Field(None, alias="_id")
    title: str
    artist: str
    album: Optional[str] = None
    mood: Optional[str] = None
    playedAt: datetime
    source: str = "manual"
    tags: List[str] = Field(default_factory=list)
    audioPath: Optional[str] = None
    embedding: Optional[List[float]] = None
    duration: Optional[float] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
