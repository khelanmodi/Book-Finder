"""Async Book model using Beanie ODM."""
from typing import Optional, List
from datetime import datetime
from beanie import Document
from pydantic import Field


class Book(Document):
    """Book document model for async DocumentDB operations with Beanie."""

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
    addedAt: datetime = Field(default_factory=datetime.utcnow)
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "books"  # Collection name in DocumentDB

        # Indexes
        indexes = [
            "genre",
            "author",
            "addedAt",
            [("title", "text"), ("author", "text")],  # Text search index
        ]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
