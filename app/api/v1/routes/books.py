"""Book management and similarity search endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.api.v1.schemas.book import (
    BookCreate, BookResponse, BookUpdate,
    SimilarBooksResponse, SimilarBook,
    TextSearchRequest, TextSearchResponse
)
from app.services.book_service import BookService
from app.services.similarity_service import SimilarityService
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/books", tags=["books"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(book_data: BookCreate):
    """
    Add a new book to the library.

    - Creates an embedding from title + description using OpenAI
    - Returns the created book with ID
    - Embedding is stored but not returned in response

    Required fields:
    - title: Book title
    - author: Author name
    - description: Book description (min 10 characters)

    Optional fields:
    - genre, isbn, publishYear, publisher, pageCount, language
    """
    book_service = BookService()

    # Convert Pydantic model to dict
    book_dict = book_data.model_dump()

    try:
        created_book = await book_service.create_book(book_dict)
        logger.info(f"Added book: {created_book['title']} by {created_book['author']}")
        return created_book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create book: {e}")
        raise HTTPException(status_code=500, detail="Failed to create book")


@router.get("/", response_model=List[BookResponse])
async def get_books(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, description="Filter by author (partial match)"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get books with optional filtering.

    - Filter by genre: GET /books?genre=Fiction
    - Filter by author: GET /books?author=Tolkien
    - Pagination: use limit and skip parameters
    - Results are sorted by addedAt (most recent first)
    """
    book_service = BookService()

    try:
        books = await book_service.get_books(
            genre=genre,
            author=author,
            limit=limit,
            skip=skip
        )
        return books
    except Exception as e:
        logger.error(f"Failed to fetch books: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch books")


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    """Get a specific book by ID."""
    book_service = BookService()

    book = await book_service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

    return book


@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(book_id: str, update_data: BookUpdate):
    """
    Update a book.

    - If title or description is updated, the embedding is automatically recreated
    - Partial updates are supported (only provide fields you want to change)
    """
    book_service = BookService()

    # Convert Pydantic model to dict, excluding unset fields
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_book = await book_service.update_book(book_id, update_dict)
    if not updated_book:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

    logger.info(f"Updated book: {book_id}")
    return updated_book


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str):
    """Delete a book from the library."""
    book_service = BookService()

    deleted = await book_service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

    logger.info(f"Deleted book: {book_id}")
    return None


@router.post("/{book_id}/similar", response_model=SimilarBooksResponse)
async def find_similar_books(
    book_id: str,
    limit: int = Query(10, le=50, description="Number of similar books to return"),
    genre_filter: Optional[str] = Query(None, description="Only search within this genre")
):
    """
    Find books similar to a given book.

    - Uses the book's embedding to find semantically similar books
    - Similarity is based on title + description content
    - Returns books sorted by similarity score (0-1, higher = more similar)
    - Optionally filter results by genre
    """
    similarity_service = SimilarityService()
    book_service = BookService()

    try:
        # Get the query book for response
        query_book = await book_service.get_book_by_id(book_id)
        if not query_book:
            raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

        # Find similar books
        similar = await similarity_service.find_similar_by_book_id(book_id, limit=limit)

        return {
            "query_book": query_book,
            "similar_books": [SimilarBook(**s) for s in similar]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        raise HTTPException(status_code=500, detail="Similarity search failed")


@router.post("/search/text", response_model=TextSearchResponse)
async def search_by_text(request: TextSearchRequest):
    """
    Search for books by text description.

    - Provide a natural language description of what you're looking for
    - Examples:
      - "coming of age story"
      - "dystopian future with rebellion"
      - "adventure in a magical world"
      - "romance set in Victorian England"
    - The API will create an embedding from your query and find semantically similar books
    - Optionally filter by genre

    Returns books sorted by similarity score (higher = more similar)
    """
    embedding_service = EmbeddingService()
    similarity_service = SimilarityService()

    try:
        # Create embedding from the user's query text
        query_embedding = embedding_service.create_embedding(request.query)

        # Find similar books
        similar = await similarity_service.find_similar_books(
            query_embedding=query_embedding,
            limit=request.limit,
            genre_filter=request.genre_filter
        )

        logger.info(f"Text search for '{request.query}' found {len(similar)} results")

        return {
            "query": request.query,
            "similar_books": [SimilarBook(**s) for s in similar]
        }

    except Exception as e:
        logger.error(f"Text search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text search failed: {str(e)}")


@router.get("/stats/embeddings")
async def get_embedding_stats():
    """
    Get statistics about book embeddings in the database.

    Returns:
    - Total books
    - Books with embeddings
    - Books without embeddings
    - Coverage percentage
    """
    similarity_service = SimilarityService()

    try:
        stats = await similarity_service.get_embedding_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get embedding stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")
