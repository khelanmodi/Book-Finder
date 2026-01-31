"""Book-related schemas for request/response validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class BookCreate(BaseModel):
    """Request schema for creating a book."""

    title: str = Field(..., min_length=1, max_length=500, description="Book title")
    author: str = Field(..., min_length=1, max_length=200, description="Author name")
    description: str = Field(..., min_length=10, description="Book description")
    genre: Optional[str] = Field(None, max_length=100, description="Genre (e.g., Fiction, Science Fiction, Mystery)")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN")
    publishYear: Optional[int] = Field(None, ge=1000, le=2100, description="Year published")
    publisher: Optional[str] = Field(None, max_length=200, description="Publisher name")
    pageCount: Optional[int] = Field(None, gt=0, description="Number of pages")
    language: Optional[str] = Field("English", max_length=50, description="Language")

    @field_validator('title', 'author', 'description')
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from text fields."""
        return v.strip() if isinstance(v, str) else v


class BookResponse(BaseModel):
    """Response schema for book queries."""

    id: str = Field(alias="_id", description="Book ID")
    title: str
    author: str
    description: str
    genre: Optional[str] = None
    isbn: Optional[str] = None
    publishYear: Optional[int] = None
    publisher: Optional[str] = None
    pageCount: Optional[int] = None
    language: Optional[str] = "English"
    addedAt: datetime
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BookUpdate(BaseModel):
    """Request schema for updating a book."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    genre: Optional[str] = Field(None, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    publishYear: Optional[int] = Field(None, ge=1000, le=2100)
    publisher: Optional[str] = Field(None, max_length=200)
    pageCount: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, max_length=50)


class SimilarBook(BaseModel):
    """Schema for a similar book result."""

    book_id: str = Field(..., description="Book ID")
    similarity_score: float = Field(..., description="Similarity score (0-1, higher = more similar)")
    book: dict = Field(..., description="Book metadata")


class SimilarBooksResponse(BaseModel):
    """Response schema for similarity search."""

    query_book: Optional[dict] = Field(None, description="Query book info (if searching by ID)")
    similar_books: List[SimilarBook] = Field(
        default_factory=list,
        description="List of similar books sorted by similarity"
    )


class TextSearchRequest(BaseModel):
    """Request schema for text-based similarity search."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Text description of what you're looking for (e.g., 'coming of age story', 'dystopian future')"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of similar books to return"
    )
    genre_filter: Optional[str] = Field(
        None,
        description="Optional genre filter to narrow results"
    )


class TextSearchResponse(BaseModel):
    """Response schema for text-based similarity search."""

    query: str = Field(..., description="The search query you provided")
    similar_books: List[SimilarBook] = Field(
        default_factory=list,
        description="List of similar books sorted by similarity"
    )
