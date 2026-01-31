"""Book data model."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Book(BaseModel):
    """Book document model matching MongoDB schema."""

    id: Optional[str] = Field(None, alias="_id")
    title: str
    author: str
    description: str
    genre: Optional[str] = None
    isbn: Optional[str] = None
    publishYear: Optional[int] = None
    publisher: Optional[str] = None
    pageCount: Optional[int] = None
    language: Optional[str] = "English"
    embedding: Optional[List[float]] = None
    addedAt: datetime
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
