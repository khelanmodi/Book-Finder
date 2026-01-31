"""Vector similarity search service using DocumentDB native vector search with async Beanie."""
import numpy as np
from typing import List, Dict, Optional
from beanie import PydanticObjectId
import logging
from app.models.book import Book

logger = logging.getLogger(__name__)


class SimilarityService:
    """Vector similarity search using DocumentDB IVF index with async Beanie."""

    async def find_similar_books(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        exclude_book_id: Optional[str] = None,
        genre_filter: Optional[str] = None,
        l_search: int = 100
    ) -> List[Dict]:
        """
        Find similar books using DocumentDB native vector search with async Beanie.

        Args:
            query_embedding: 1536-dimensional numpy array (OpenAI embedding)
            limit: Number of results to return (k)
            exclude_book_id: Book ID to exclude from results (when searching by existing book)
            genre_filter: Optional genre filter
            l_search: Size of dynamic candidate list (default: 100, range: 10-1000)

        Returns:
            List of dicts with:
            - book_id: MongoDB ObjectId as string
            - similarity_score: Float between 0 and 1 (1 = identical)
            - book: Book metadata (title, author, description, genre)
        """
        # Convert numpy array to list for MongoDB query
        query_vector = query_embedding.tolist()

        # Build filter for cosmosSearch
        filters = []
        if exclude_book_id:
            try:
                filters.append({"_id": {"$ne": PydanticObjectId(exclude_book_id)}})
            except Exception as e:
                logger.warning(f"Invalid book ID format: {exclude_book_id}")

        if genre_filter:
            filters.append({"genre": {"$eq": genre_filter}})

        # Build aggregation pipeline with $search stage
        pipeline = [
            {
                "$search": {
                    "cosmosSearch": {
                        "path": "embedding",
                        "vector": query_vector,
                        "k": limit,
                        "lSearch": max(limit, l_search)  # lSearch must be >= k
                    }
                }
            }
        ]

        # Add filter stage if there are filters
        if filters:
            if len(filters) == 1:
                pipeline.append({"$match": filters[0]})
            else:
                pipeline.append({"$match": {"$and": filters}})

        # Add projection to include similarity score
        pipeline.append({
            "$project": {
                "_id": 1,
                "title": 1,
                "author": 1,
                "description": 1,
                "genre": 1,
                "publishYear": 1,
                "isbn": 1,
                "similarityScore": {"$meta": "searchScore"}
            }
        })

        try:
            # Execute vector search using Beanie's aggregate
            results = await Book.aggregate(pipeline).to_list()

            # Format results
            similarities = []
            for result in results:
                # Truncate description for response
                description = result.get('description', '')
                truncated_desc = description[:200] + '...' if len(description) > 200 else description

                similarities.append({
                    'book_id': str(result['_id']),
                    'similarity_score': float(result.get('similarityScore', 0)),
                    'book': {
                        'title': result.get('title', 'Unknown'),
                        'author': result.get('author', 'Unknown'),
                        'description': truncated_desc,
                        'genre': result.get('genre'),
                        'publishYear': result.get('publishYear'),
                        'isbn': result.get('isbn')
                    }
                })

            logger.info(
                f"Vector search found {len(similarities)} similar books "
                f"(k={limit}, lSearch={l_search})"
            )

            return similarities

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise

    async def find_similar_by_book_id(
        self,
        book_id: str,
        limit: int = 10,
        l_search: int = 100
    ) -> List[Dict]:
        """
        Find similar books given a book ID using DocumentDB vector search with async Beanie.

        Args:
            book_id: MongoDB ObjectId as string
            limit: Number of results to return (k)
            l_search: Size of dynamic candidate list for search

        Returns:
            List of similar books with similarity scores

        Raises:
            ValueError: If book not found or has no embedding
        """
        # Fetch the reference book using Beanie
        try:
            book = await Book.get(PydanticObjectId(book_id))
        except Exception as e:
            raise ValueError(f"Invalid book ID: {book_id}") from e

        if not book:
            raise ValueError(f"Book not found: {book_id}")

        if not book.embedding:
            raise ValueError(f"Book {book_id} has no embedding")

        # Convert embedding to numpy array
        query_embedding = np.array(book.embedding)

        logger.info(
            f"Vector search for books similar to: "
            f"{book.title} by {book.author}"
        )

        # Find similar books using native vector search (excluding the query book itself)
        return await self.find_similar_books(
            query_embedding,
            limit=limit,
            exclude_book_id=book_id,
            l_search=l_search
        )

    async def get_embedding_stats(self) -> Dict:
        """
        Get statistics about embeddings in the database using async Beanie.

        Returns:
            Dictionary with:
            - total_books: Total number of books
            - books_with_embeddings: Number of books with embeddings
            - books_without_embeddings: Number of books without embeddings
            - coverage: Percentage of books with embeddings
        """
        total = await Book.count()
        with_embeddings = await Book.find(
            {"embedding": {"$exists": True, "$ne": None}}
        ).count()
        without_embeddings = total - with_embeddings

        coverage = (with_embeddings / total * 100) if total > 0 else 0

        return {
            'total_books': total,
            'books_with_embeddings': with_embeddings,
            'books_without_embeddings': without_embeddings,
            'coverage_percentage': round(coverage, 2)
        }
