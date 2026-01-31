"""Import books from JSON file or direct JSON data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
import logging
from app.core.database import db
from app.services.book_service import BookService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_books_from_json(books_data):
    """
    Import books from JSON data with OpenAI embeddings.

    Args:
        books_data: List of dicts with title, author, description
    """
    logger.info("Connecting to database...")
    db.connect()

    book_service = BookService()
    inserted_count = 0
    failed_count = 0

    total = len(books_data)
    logger.info(f"\n📚 Importing {total} books with OpenAI embeddings...")
    logger.info("⏳ This will make API calls to OpenAI (may take 2-3 minutes)...\n")

    for i, book_data in enumerate(books_data, 1):
        try:
            # Add timestamp
            book_data['addedAt'] = datetime.utcnow()

            # Validate required fields
            if not all(k in book_data for k in ['title', 'author', 'description']):
                logger.warning(f"⚠️  [{i}/{total}] Skipping book (missing fields): {book_data.get('title', 'Unknown')}")
                failed_count += 1
                continue

            # Create book (this will create embedding via OpenAI)
            created_book = book_service.create_book(book_data)
            inserted_count += 1

            logger.info(
                f"✓ [{inserted_count}/{total}] {book_data['title'][:50]} by {book_data['author'][:30]}"
            )

        except Exception as e:
            failed_count += 1
            logger.error(f"✗ [{i}/{total}] Failed: {book_data.get('title', 'Unknown')} - {str(e)[:100]}")
            continue

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Import Complete!")
    logger.info(f"{'='*60}")
    logger.info(f"  ✓ Successfully imported: {inserted_count} books")
    if failed_count > 0:
        logger.info(f"  ✗ Failed: {failed_count} books")

    # Show statistics
    books_collection = db.get_books_collection()
    total_books = books_collection.count_documents({})
    with_embeddings = books_collection.count_documents({"embedding": {"$exists": True}})

    logger.info(f"\n📊 Database Statistics:")
    logger.info(f"  Total books: {total_books}")
    logger.info(f"  Books with embeddings: {with_embeddings}")
    logger.info(f"  Coverage: {(with_embeddings/total_books*100):.1f}%")

    # Show top authors
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_authors = list(books_collection.aggregate(pipeline))

    if top_authors:
        logger.info(f"\n📖 Top Authors:")
        for author_stat in top_authors:
            logger.info(f"  {author_stat['_id']}: {author_stat['count']} books")

    db.close()


def main():
    """Main entry point - can load from file or use inline JSON."""

    # Option 1: Load from file
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        logger.info(f"Loading books from file: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            books_data = json.load(f)
        import_books_from_json(books_data)

    # Option 2: Paste your JSON here directly
    else:
        logger.info("Using inline JSON data...")

        # PASTE YOUR JSON HERE:
        books_data = [
          {
            "title": "1984",
            "author": "George Orwell",
            "description": "A dystopian tale of totalitarian surveillance and control, introducing 'Big Brother' into popular culture."
          },
          {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "description": "A young girl's perspective on racial injustice and moral growth in the American South during a trial."
          },
          {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A critique of the Jazz Age's excess through a millionaire's doomed pursuit of lost love."
          },
          {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": "Elizabeth Bennet navigates love, class, and misconceptions with the proud Mr. Darcy."
          },
          {
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "description": "A disillusioned teen's odyssey through New York, capturing alienation and adolescence."
          },
          {
            "title": "Don Quixote",
            "author": "Miguel de Cervantes",
            "description": "A delusional knight's adventures blur reality and fantasy in Spain's golden age."
          },
          {
            "title": "The Lord of the Rings",
            "author": "J.R.R. Tolkien",
            "description": "An epic quest to destroy a corrupting ring and defeat dark forces in Middle-earth."
          },
          {
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "description": "An orphaned boy discovers he's a wizard and uncovers his destiny at Hogwarts."
          },
          {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "description": "A reluctant hobbit joins dwarves to reclaim treasure from a dragon."
          },
          {
            "title": "One Hundred Years of Solitude",
            "author": "Gabriel García Márquez",
            "description": "The Buendía family's saga in magical realist Macondo spans generations."
          },
          {
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "description": "A engineered society trades freedom for stability and pleasure."
          },
          {
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "description": "A shepherd pursues his 'personal legend' across deserts in search of treasure."
          },
          {
            "title": "Things Fall Apart",
            "author": "Chinua Achebe",
            "description": "An Igbo warrior resists British colonialism's erosion of his culture."
          },
          {
            "title": "Beloved",
            "author": "Toni Morrison",
            "description": "A former slave confronts the haunting legacy of trauma and infanticide."
          },
          {
            "title": "The Adventures of Huckleberry Finn",
            "author": "Mark Twain",
            "description": "A boy and runaway slave raft down the Mississippi, challenging racism."
          },
          {
            "title": "The Da Vinci Code",
            "author": "Dan Brown",
            "description": "A symbologist unravels religious conspiracies through cryptic clues."
          },
          {
            "title": "War and Peace",
            "author": "Leo Tolstoy",
            "description": "Russian aristocracy amid Napoleon's invasion explores history and fate."
          },
          {
            "title": "The Brothers Karamazov",
            "author": "Fyodor Dostoevsky",
            "description": "Brothers grapple with patricide, faith, and morality in Russia."
          },
          {
            "title": "Moby-Dick",
            "author": "Herman Melville",
            "description": "Captain Ahab's obsessive hunt for a white whale delves into obsession."
          },
          {
            "title": "The Little Prince",
            "author": "Antoine de Saint-Exupéry",
            "description": "A pilot meets a childlike prince exploring planets and human folly."
          },
          {
            "title": "Animal Farm",
            "author": "George Orwell",
            "description": "Farm animals' revolution satirizes Stalinism and power corruption."
          },
          {
            "title": "The Hunger Games",
            "author": "Suzanne Collins",
            "description": "Teens fight to survive in a televised dystopian battle royale."
          },
          {
            "title": "The Book Thief",
            "author": "Markus Zusak",
            "description": "A girl steals books in Nazi Germany amid death and words' power."
          },
          {
            "title": "Fahrenheit 451",
            "author": "Ray Bradbury",
            "description": "Firemen burn books in a censored future, sparking rebellion."
          },
          {
            "title": "Jane Eyre",
            "author": "Charlotte Brontë",
            "description": "A governess uncovers secrets and finds love at a mysterious estate."
          },
          {
            "title": "Wuthering Heights",
            "author": "Emily Brontë",
            "description": "Vengeful love haunts the moors across generations."
          },
          {
            "title": "The Picture of Dorian Gray",
            "author": "Oscar Wilde",
            "description": "A portrait ages while its subject indulges eternally youthful vices."
          },
          {
            "title": "Slaughterhouse-Five",
            "author": "Kurt Vonnegut",
            "description": "A soldier time-travels through WWII Dresden's bombing horrors."
          },
          {
            "title": "The Grapes of Wrath",
            "author": "John Steinbeck",
            "description": "Dust Bowl migrants seek dignity amid exploitation."
          },
          {
            "title": "Lord of the Flies",
            "author": "William Golding",
            "description": "Stranded boys descend into savagery without civilization."
          },
          {
            "title": "The Outsiders",
            "author": "S.E. Hinton",
            "description": "Teen greasers vs. socs clash in class warfare."
          },
          {
            "title": "Charlotte's Web",
            "author": "E.B. White",
            "description": "A pig and spider's friendship defies fate on a farm."
          },
          {
            "title": "The Giver",
            "author": "Lois Lowry",
            "description": "A boy uncovers his society's dark secrets of sameness."
          },
          {
            "title": "Of Mice and Men",
            "author": "John Steinbeck",
            "description": "Two migrant workers dream big but face harsh realities."
          },
          {
            "title": "The Fault in Our Stars",
            "author": "John Green",
            "description": "Teens with cancer find love and meaning."
          },
          {
            "title": "Night",
            "author": "Elie Wiesel",
            "description": "A Holocaust survivor's memoir of Auschwitz horrors."
          },
          {
            "title": "The Diary of a Young Girl",
            "author": "Anne Frank",
            "description": "A Jewish teen's annex-hidden writings during Nazi occupation."
          },
          {
            "title": "A Game of Thrones",
            "author": "George R.R. Martin",
            "description": "Noble houses vie for Westeros' iron throne."
          },
          {
            "title": "The Girl on the Train",
            "author": "Paula Hawkins",
            "description": "A commuter witnesses a disappearance, unraveling lies."
          },
          {
            "title": "The Shining",
            "author": "Stephen King",
            "description": "A family's isolated hotel unleashes madness and ghosts."
          },
          {
            "title": "The Kite Runner",
            "author": "Khaled Hosseini",
            "description": "Afghan boy's betrayal and redemption amid war."
          },
          {
            "title": "Life of Pi",
            "author": "Yann Martel",
            "description": "Shipwrecked boy survives with a tiger, questioning faith."
          },
          {
            "title": "The Road",
            "author": "Cormac McCarthy",
            "description": "Father and son trek a post-apocalyptic wasteland."
          },
          {
            "title": "Gone Girl",
            "author": "Gillian Flynn",
            "description": "A wife's disappearance exposes a twisted marriage."
          },
          {
            "title": "The Handmaid's Tale",
            "author": "Margaret Atwood",
            "description": "Women subjugated in a theocratic regime."
          },
          {
            "title": "Dune",
            "author": "Frank Herbert",
            "description": "Heir battles for a desert planet's spice control."
          },
          {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "description": "Wizard's legendary life story unfolds."
          },
          {
            "title": "Where the Crawdads Sing",
            "author": "Delia Owens",
            "description": "Marsh girl's isolation and murder mystery."
          },
          {
            "title": "Atomic Habits",
            "author": "James Clear",
            "description": "Practical guide to building lasting habits."
          },
          {
            "title": "Sapiens",
            "author": "Yuval Noah Harari",
            "description": "Human history from cognitive revolution to today."
          }
        ]

        import_books_from_json(books_data)


if __name__ == "__main__":
    main()
