"""Book service for CRUD operations with async Beanie."""
from typing import List, Dict, Optional
from datetime import datetime
from beanie import PydanticObjectId
import logging
from app.models.book import Book
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class BookService:
    """Business logic for book operations using async Beanie."""

    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def create_book(self, book_data: Dict) -> Dict:
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

        # Insert into database using Beanie
        book = Book(**book_data)
        await book.insert()

        logger.info(
            f"Created book: {book.title} by {book.author} "
            f"(ID: {book.id})"
        )

        return self._serialize_book(book)

    async def get_book_by_id(self, book_id: str) -> Optional[Dict]:
        """
        Get a book by ID.

        Args:
            book_id: MongoDB ObjectId as string

        Returns:
            Book document or None if not found
        """
        try:
            book = await Book.get(PydanticObjectId(book_id))
            if book:
                return self._serialize_book(book)
            return None
        except Exception as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            return None

    async def get_books(
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
        # Build query using Beanie
        query = Book.find()

        if genre:
            query = query.find(Book.genre == genre)
        if author:
            # Case-insensitive regex search
            query = query.find({"author": {"$regex": author, "$options": "i"}})

        # Execute query with sorting, skip, and limit
        books = await query.sort(-Book.addedAt).skip(skip).limit(limit).to_list()

        logger.info(
            f"Retrieved {len(books)} books "
            f"(genre={genre}, author={author}, limit={limit}, skip={skip})"
        )

        return [self._serialize_book(book) for book in books]

    async def update_book(self, book_id: str, update_data: Dict) -> Optional[Dict]:
        """
        Update a book. If title or description changed, recreate embedding.

        Args:
            book_id: MongoDB ObjectId as string
            update_data: Fields to update

        Returns:
            Updated book document or None if not found
        """
        try:
            # Get current book
            book = await Book.get(PydanticObjectId(book_id))
            if not book:
                return None

            # Add updatedAt timestamp
            update_data['updatedAt'] = datetime.utcnow()

            # If title or description changed, recreate embedding
            if 'title' in update_data or 'description' in update_data:
                new_title = update_data.get('title', book.title)
                new_desc = update_data.get('description', book.description)

                try:
                    embedding = self.embedding_service.create_book_embedding(new_title, new_desc)
                    update_data['embedding'] = embedding.tolist()
                    logger.info(f"Recreated embedding for updated book: {book_id}")
                except Exception as e:
                    logger.error(f"Failed to recreate embedding: {e}")

            # Update fields
            for key, value in update_data.items():
                setattr(book, key, value)

            # Save to database
            await book.save()
            logger.info(f"Updated book: {book_id}")

            return self._serialize_book(book)

        except Exception as e:
            logger.error(f"Error updating book {book_id}: {e}")
            return None

    async def delete_book(self, book_id: str) -> bool:
        """
        Delete a book.

        Args:
            book_id: MongoDB ObjectId as string

        Returns:
            True if deleted, False otherwise
        """
        try:
            book = await Book.get(PydanticObjectId(book_id))
            if book:
                await book.delete()
                logger.info(f"Deleted book: {book_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {e}")
            return False

    async def get_book_count(self, genre: Optional[str] = None) -> int:
        """
        Get count of books, optionally filtered by genre.

        Args:
            genre: Filter by genre

        Returns:
            Number of books
        """
        if genre:
            return await Book.find(Book.genre == genre).count()
        else:
            return await Book.count()

    @staticmethod
    def _serialize_book(book) -> Dict:
        """
        Serialize book document for JSON response.

        Args:
            book: Beanie Book document

        Returns:
            Serialized book with _id as string
        """
        if isinstance(book, Book):
            # Beanie Document - convert to dict
            book_dict = book.dict()
            book_dict['_id'] = str(book.id)

            # Remove embedding from response (too large)
            if 'embedding' in book_dict:
                del book_dict['embedding']

            # Remove Beanie internal fields
            book_dict.pop('id', None)
            book_dict.pop('revision_id', None)

            return book_dict

        # Fallback for dict (shouldn't happen with Beanie)
        if isinstance(book, dict):
            if '_id' in book:
                book['_id'] = str(book['_id'])
            if 'embedding' in book:
                del book['embedding']
            return book

        return {}
