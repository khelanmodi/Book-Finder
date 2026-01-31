"""Create DiskANN vector index for book similarity search."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from app.core.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_vector_index():
    """Create DiskANN vector index on book embeddings."""
    logger.info("Connecting to database...")
    db.connect()

    try:
        # Create DiskANN vector index on embedding field
        logger.info("Creating DiskANN vector index on 'embedding' field...")

        result = db.db.command({
            "createIndexes": "books",
            "indexes": [
                {
                    "name": "bookEmbeddingIndex",
                    "key": {
                        "embedding": "cosmosSearch"
                    },
                    "cosmosSearchOptions": {
                        "kind": "vector-diskann",
                        "dimensions": 1536,  # OpenAI text-embedding-3-small
                        "similarity": "COS",  # Cosine similarity
                        "maxDegree": 32,      # Balance between accuracy and performance
                        "lBuild": 64          # Higher value for better index quality
                    }
                }
            ]
        })

        logger.info("✅ Vector index created successfully!")
        logger.info(f"Result: {result}")

        # Verify index was created
        logger.info("\nVerifying indexes...")
        indexes = list(db.db.books.list_indexes())

        logger.info(f"\n📋 Current indexes on 'books' collection:")
        for idx in indexes:
            logger.info(f"  - {idx.get('name', 'unknown')}")
            if 'cosmosSearchOptions' in idx:
                logger.info(f"    Type: {idx['cosmosSearchOptions']['kind']}")
                logger.info(f"    Dimensions: {idx['cosmosSearchOptions']['dimensions']}")
                logger.info(f"    Similarity: {idx['cosmosSearchOptions']['similarity']}")

    except Exception as e:
        logger.error(f"Failed to create vector index: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_vector_index()
