"""Embedding service using OpenAI API for text embeddings."""
import numpy as np
from typing import List
import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Create text embeddings using OpenAI API."""

    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.OPENAI_KEY:
            raise ValueError("OPENAI_KEY not found in environment variables")

        self.client = OpenAI(api_key=settings.OPENAI_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.embedding_dim = settings.EMBEDDING_DIM

    def create_embedding(self, text: str) -> np.ndarray:
        """
        Create embedding vector from text using OpenAI API.

        Args:
            text: Input text (book title + description)

        Returns:
            numpy array of embedding (1536 dimensions for text-embedding-3-small)
        """
        try:
            # Clean text
            text = text.strip()
            if not text:
                raise ValueError("Text cannot be empty")

            # Call OpenAI API
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )

            # Extract embedding
            embedding = response.data[0].embedding
            embedding_array = np.array(embedding, dtype=np.float32)

            logger.info(f"Created embedding for text (length: {len(text)} chars, dim: {len(embedding_array)})")

            return embedding_array

        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise

    def create_book_embedding(self, title: str, description: str) -> np.ndarray:
        """
        Create embedding for a book from title and description.

        Args:
            title: Book title
            description: Book description

        Returns:
            Embedding vector (numpy array)
        """
        # Combine title and description
        # Format: "Title. Description"
        # This gives more weight to both title and content
        combined_text = f"{title}. {description}"

        logger.info(f"Creating embedding for book: {title[:50]}...")

        return self.create_embedding(combined_text)

    def create_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Create embeddings for multiple texts (batch processing).

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        try:
            # OpenAI API supports batch processing
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embeddings = [
                np.array(item.embedding, dtype=np.float32)
                for item in response.data
            ]

            logger.info(f"Created {len(embeddings)} embeddings in batch")

            return embeddings

        except Exception as e:
            logger.error(f"Failed to create batch embeddings: {e}")
            raise

    def validate_embedding(self, embedding: np.ndarray) -> bool:
        """
        Validate embedding dimensions and format.

        Args:
            embedding: Embedding vector to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(embedding, np.ndarray):
            logger.warning("Embedding is not a numpy array")
            return False

        if embedding.shape[0] != self.embedding_dim:
            logger.warning(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {embedding.shape[0]}")
            return False

        if not np.isfinite(embedding).all():
            logger.warning("Embedding contains non-finite values")
            return False

        return True
