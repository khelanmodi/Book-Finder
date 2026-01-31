"""Async database connection using Motor and Beanie."""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class AsyncDatabase:
    """Async DocumentDB database connection manager using Motor."""

    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    async def connect(self):
        """Initialize async DocumentDB connection and setup Beanie."""
        try:
            # Create async Motor client
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000
            )

            # Test connection (async!)
            await self.client.admin.command('ping')

            self.db = self.client[settings.DB_NAME]

            # Initialize Beanie with document models
            from app.models.book import Book  # Import here to avoid circular imports
            await init_beanie(database=self.db, document_models=[Book])

            logger.info(f"Connected to DocumentDB: {settings.DB_NAME}")

        except Exception as e:
            logger.error(f"Failed to connect to DocumentDB: {e}")
            raise

    async def close(self):
        """Close async DocumentDB connection."""
        if self.client is not None:
            self.client.close()
            logger.info("DocumentDB connection closed")

    async def ping(self):
        """Ping the database to check connection."""
        if self.client is None:
            raise RuntimeError("Database not connected")
        result = await self.client.admin.command('ping')
        return result


# Singleton instance
db = AsyncDatabase()
