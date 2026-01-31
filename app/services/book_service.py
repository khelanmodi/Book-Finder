"""Book service for CRUD operations."""
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
import logging
from app.core.database import db
from app.models.book import Book
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class BookService:
    """Business logic for book operations."""

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def create_book(self, book_data: Dict) -> Dict:
        """
        Create a new book in the database with embedding.

        Args:
            book_data: Dictionary with book fields

        Returns:
            Created book document with _id and embedding

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        required_fields = ['title', 'author', 'description']
        for field in required_fields:
            if field not in book_data or not book_data[field]:
                raise ValueError(f"Missing required field: {field}")

        # Set defaults
        now = datetime.utcnow()
        book_data.setdefault('addedAt', now)
        book_data.setdefault('createdAt', now)
        book_data.setdefault('updatedAt', now)
        book_data.setdefault('language', 'English')

        # Create embedding from title + description
        try:
            embedding = self.embedding_service.create_book_embedding(
                title=book_data['title'],
                description=book_data['description']
            )
            book_data['embedding'] = embedding.tolist()
            logger.info(f"Created embedding for book: {book_data['title']}")
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise ValueError(f"Failed to create embedding: {str(e)}")

        # Insert into database
        books_collection = db.get_books_collection()
        result = books_collection.insert_one(book_data)

        # Fetch the created document
        created_book = books_collection.find_one({"_id": result.inserted_id})

        logger.info(
            f"Created book: {created_book['title']} by {created_book['author']} "
            f"(ID: {result.inserted_id})"
        )

        return self._serialize_book(created_book)

    def get_book_by_id(self, book_id: str) -> Optional[Dict]:
        """
        Get a book by ID.

        Args:
            book_id: MongoDB ObjectId as string

        Returns:
            Book document or None if not found
        """
        books_collection = db.get_books_collection()

        try:
            book = books_collection.find_one({"_id": ObjectId(book_id)})
            if book:
                return self._serialize_book(book)
            return None
        except Exception as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            return None

    def get_books(
        self,
        genre: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict]:
        """
        Get books with optional filtering.

        Args:
            genre: Filter by genre
            author: Filter by author (case-insensitive partial match)
            limit: Maximum number of results
            skip: Number of results to skip (pagination)

        Returns:
            List of book documents
        """
        books_collection = db.get_books_collection()

        # Build query
        query = {}
        if genre:
            query['genre'] = genre
        if author:
            # Case-insensitive regex search
            query['author'] = {"$regex": author, "$options": "i"}

        # Execute query with sorting
        cursor = books_collection.find(query).sort("addedAt", -1).skip(skip).limit(limit)
        books = list(cursor)

        logger.info(
            f"Retrieved {len(books)} books "
            f"(genre={genre}, author={author}, limit={limit}, skip={skip})"
        )

        return [self._serialize_book(book) for book in books]

    def update_book(self, book_id: str, update_data: Dict) -> Optional[Dict]:
        """
        Update a book. If title or description changed, recreate embedding.

        Args:
            book_id: MongoDB ObjectId as string
            update_data: Fields to update

        Returns:
            Updated book document or None if not found
        """
        books_collection = db.get_books_collection()

        # Add updatedAt timestamp
        update_data['updatedAt'] = datetime.utcnow()

        # If title or description changed, recreate embedding
        if 'title' in update_data or 'description' in update_data:
            # Get current book
            current_book = books_collection.find_one({"_id": ObjectId(book_id)})
            if current_book:
                new_title = update_data.get('title', current_book.get('title'))
                new_desc = update_data.get('description', current_book.get('description'))

                try:
                    embedding = self.embedding_service.create_book_embedding(new_title, new_desc)
                    update_data['embedding'] = embedding.tolist()
                    logger.info(f"Recreated embedding for updated book: {book_id}")
                except Exception as e:
                    logger.error(f"Failed to recreate embedding: {e}")

        try:
            result = books_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                updated_book = books_collection.find_one({"_id": ObjectId(book_id)})
                logger.info(f"Updated book: {book_id}")
                return self._serialize_book(updated_book)

            return None

        except Exception as e:
            logger.error(f"Error updating book {book_id}: {e}")
            return None

    def delete_book(self, book_id: str) -> bool:
        """
        Delete a book.

        Args:
            book_id: MongoDB ObjectId as string

        Returns:
            True if deleted, False otherwise
        """
        books_collection = db.get_books_collection()

        try:
            result = books_collection.delete_one({"_id": ObjectId(book_id)})
            if result.deleted_count > 0:
                logger.info(f"Deleted book: {book_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {e}")
            return False

    def get_book_count(self, genre: Optional[str] = None) -> int:
        """
        Get count of books, optionally filtered by genre.

        Args:
            genre: Filter by genre

        Returns:
            Number of books
        """
        books_collection = db.get_books_collection()
        query = {"genre": genre} if genre else {}
        return books_collection.count_documents(query)

    @staticmethod
    def _serialize_book(book: Dict) -> Dict:
        """
        Serialize book document for JSON response.

        Args:
            book: MongoDB book document

        Returns:
            Serialized book with _id as string
        """
        if book and '_id' in book:
            book['_id'] = str(book['_id'])

        # Remove embedding from response (too large)
        if 'embedding' in book:
            del book['embedding']

        return book
