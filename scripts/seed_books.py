"""Seed database with sample books."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import random
import logging
from app.core.database import db
from app.services.book_service import BookService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample books with descriptions
SAMPLE_BOOKS = [
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "description": "Bilbo Baggins, a respectable hobbit, is swept into an epic quest to reclaim the lost Dwarf Kingdom of Erebor from the fearsome dragon Smaug. This fantasy adventure follows an unlikely hero through Middle-earth, encountering trolls, goblins, and the mysterious creature Gollum.",
        "genre": "Fantasy",
        "publishYear": 1937,
        "pageCount": 310
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "description": "In a dystopian future where totalitarian regime exercises complete control, Winston Smith works for the Ministry of Truth rewriting history. This political fiction explores themes of surveillance, propaganda, and the power of language in a society where Big Brother is always watching.",
        "genre": "Dystopian Fiction",
        "publishYear": 1949,
        "pageCount": 328
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "description": "Set in the Depression-era South, this classic novel follows young Scout Finch as her father, lawyer Atticus Finch, defends a Black man falsely accused of assaulting a white woman. The story explores themes of racial injustice, moral growth, and compassion through a child's eyes.",
        "genre": "Southern Gothic",
        "publishYear": 1960,
        "pageCount": 281
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "description": "Elizabeth Bennet must navigate the complexities of manners, morality, and matrimony in Georgian England. This romantic novel follows her relationship with the proud Mr. Darcy, exploring themes of social class, reputation, and the importance of marrying for love rather than money.",
        "genre": "Romance",
        "publishYear": 1813,
        "pageCount": 432
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "description": "Nick Carraway narrates the story of Jay Gatsby's obsessive pursuit of wealth and lost love in 1920s New York. This Jazz Age novel critiques the American Dream through lavish parties, tragic romance, and the hollow pursuit of material success.",
        "genre": "Literary Fiction",
        "publishYear": 1925,
        "pageCount": 180
    },
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "description": "Young Paul Atreides becomes embroiled in a complex political struggle for control of the desert planet Arrakis, the only source of the universe's most valuable substance. This epic science fiction explores ecology, religion, politics, and human evolution in a richly detailed future universe.",
        "genre": "Science Fiction",
        "publishYear": 1965,
        "pageCount": 688
    },
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J.K. Rowling",
        "description": "An orphaned boy discovers he's a wizard on his eleventh birthday and enters Hogwarts School of Witchcraft and Wizardry. This fantasy adventure follows Harry's first year learning magic, making friends, and uncovering secrets about his past and his nemesis, Lord Voldemort.",
        "genre": "Fantasy",
        "publishYear": 1997,
        "pageCount": 223
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "description": "Holden Caulfield narrates his experiences after being expelled from prep school, wandering through New York City. This coming-of-age novel explores teenage alienation, loss of innocence, and the phoniness of adult society through the voice of an iconic unreliable narrator.",
        "genre": "Literary Fiction",
        "publishYear": 1951,
        "pageCount": 277
    },
    {
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "description": "Frodo Baggins must destroy a powerful ring to save Middle-earth from the Dark Lord Sauron. This epic fantasy follows a fellowship of heroes through a perilous journey, exploring themes of friendship, sacrifice, and the corruption of power.",
        "genre": "Fantasy",
        "publishYear": 1954,
        "pageCount": 1178
    },
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "description": "In a technologically advanced future society where humans are genetically bred and conditioned for specific roles, one man questions the price of stability and happiness. This dystopian novel explores themes of technology, individuality, and the cost of a perfect society.",
        "genre": "Dystopian Fiction",
        "publishYear": 1932,
        "pageCount": 268
    }
]


def seed_books():
    """Seed database with sample books including embeddings."""
    logger.info("Connecting to database...")
    db.connect()

    book_service = BookService()
    inserted_count = 0

    logger.info(f"Adding {len(SAMPLE_BOOKS)} books with OpenAI embeddings...")
    logger.info("Note: This will make API calls to OpenAI and may take a minute...\n")

    for book in SAMPLE_BOOKS:
        try:
            # Add some variation to addedAt
            days_ago = random.randint(0, 30)
            book['addedAt'] = datetime.utcnow() - timedelta(days=days_ago)

            # Create book (this will create embedding via OpenAI)
            created_book = book_service.create_book(book)
            inserted_count += 1

            logger.info(
                f"✓ [{inserted_count}/{len(SAMPLE_BOOKS)}] Added: {book['title']} by {book['author']}"
            )

        except Exception as e:
            logger.error(f"✗ Failed to add '{book['title']}': {e}")
            continue

    logger.info(f"\n✓ Successfully seeded {inserted_count} books!")

    # Show statistics
    books_collection = db.get_books_collection()
    total = books_collection.count_documents({})
    with_embeddings = books_collection.count_documents({"embedding": {"$exists": True}})

    logger.info("\nDatabase statistics:")
    logger.info(f"  Total books: {total}")
    logger.info(f"  Books with embeddings: {with_embeddings}")
    logger.info(f"  Coverage: {(with_embeddings/total*100):.1f}%")

    # Show genre distribution
    pipeline = [
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    genres = list(books_collection.aggregate(pipeline))

    logger.info("\n  Genre distribution:")
    for genre_stat in genres:
        logger.info(f"    {genre_stat['_id']}: {genre_stat['count']}")

    db.close()


if __name__ == "__main__":
    seed_books()
