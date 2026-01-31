"""Database connection and index management."""
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """DocumentDB database connection manager."""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self):
        """Initialize DocumentDB connection and create indexes."""
        try:
            self.client = MongoClient(
                settings.MONGODB_URL,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000
            )

            # Test connection
            self.client.admin.command('ping')

            self.db = self.client[settings.DB_NAME]

            # Create indexes
            self._create_indexes()

            logger.info(f"Connected to DocumentDB: {settings.DB_NAME}")

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to DocumentDB: {e}")
            raise

    def _create_indexes(self):
        """Create database indexes (idempotent)."""
        books = self.db.books

        # Compound indexes for efficient queries
        books.create_index([("genre", ASCENDING), ("addedAt", DESCENDING)])
        books.create_index([("author", ASCENDING), ("addedAt", DESCENDING)])
        books.create_index([("addedAt", DESCENDING)])
        books.create_index([("title", "text"), ("author", "text")])  # Text search

        logger.info("Database indexes created successfully")

    def close(self):
        """Close DocumentDB connection."""
        if self.client is not None:
            self.client.close()
            logger.info("DocumentDB connection closed")

    def get_books_collection(self):
        """Get books collection."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        return self.db.books


# Singleton instance
db = Database()
