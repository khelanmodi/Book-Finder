"""Seed database with sample tracks for testing."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import random
from app.core.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample track data
SAMPLE_TRACKS = [
    # Focus mood
    {
        "title": "Midnight Study Session",
        "artist": "Lo-Fi Beats Collective",
        "album": "Study Vibes Vol. 1",
        "mood": "focus",
        "tags": ["lofi", "instrumental", "study", "calm"],
        "source": "manual"
    },
    {
        "title": "Deep Work Flow",
        "artist": "Ambient Sounds",
        "album": "Productivity",
        "mood": "focus",
        "tags": ["ambient", "focus", "concentration"],
        "source": "manual"
    },
    {
        "title": "Coding in the Rain",
        "artist": "ChillHop Music",
        "album": "Rainy Day Sessions",
        "mood": "focus",
        "tags": ["lofi", "rain", "coding", "chill"],
        "source": "manual"
    },
    # Energetic mood
    {
        "title": "Energy Boost",
        "artist": "EDM Collective",
        "album": "Festival Anthems 2024",
        "mood": "energetic",
        "tags": ["edm", "upbeat", "dance", "party"],
        "source": "manual"
    },
    {
        "title": "Workout Motivation",
        "artist": "Fitness Beats",
        "album": "Gym Sessions",
        "mood": "energetic",
        "tags": ["workout", "high-energy", "pump"],
        "source": "manual"
    },
    {
        "title": "Electric Dreams",
        "artist": "Synthwave Masters",
        "album": "Neon Nights",
        "mood": "energetic",
        "tags": ["synthwave", "electronic", "upbeat"],
        "source": "manual"
    },
    # Chill mood
    {
        "title": "Sunday Morning",
        "artist": "Jazz Cafe",
        "album": "Lazy Sundays",
        "mood": "chill",
        "tags": ["jazz", "chill", "relaxing", "acoustic"],
        "source": "manual"
    },
    {
        "title": "Ocean Breeze",
        "artist": "Nature Sounds",
        "album": "Coastal Vibes",
        "mood": "chill",
        "tags": ["chill", "nature", "relaxing"],
        "source": "manual"
    },
    {
        "title": "Late Night Drive",
        "artist": "Downtempo Collective",
        "album": "After Hours",
        "mood": "chill",
        "tags": ["downtempo", "chill", "night"],
        "source": "manual"
    },
    # Melancholic mood
    {
        "title": "Rainy Day Blues",
        "artist": "Indie Folk Artists",
        "album": "Melancholy",
        "mood": "melancholic",
        "tags": ["sad", "emotional", "rain", "folk"],
        "source": "manual"
    },
    {
        "title": "Memories Fade",
        "artist": "Piano Soloist",
        "album": "Reflections",
        "mood": "melancholic",
        "tags": ["piano", "sad", "nostalgic", "instrumental"],
        "source": "manual"
    },
    # Happy mood
    {
        "title": "Good Vibes Only",
        "artist": "Pop Stars",
        "album": "Summer Hits",
        "mood": "happy",
        "tags": ["pop", "happy", "uplifting", "feel-good"],
        "source": "manual"
    },
    {
        "title": "Sunshine Day",
        "artist": "Feel Good Band",
        "album": "Positive Energy",
        "mood": "happy",
        "tags": ["happy", "sunshine", "cheerful"],
        "source": "manual"
    },
    # More artists for top artists test
    {
        "title": "Feather",
        "artist": "Nujabes",
        "album": "Modal Soul",
        "mood": "chill",
        "tags": ["hip-hop", "jazz", "instrumental", "lofi"],
        "source": "manual"
    },
    {
        "title": "Aruarian Dance",
        "artist": "Nujabes",
        "album": "Samurai Champloo",
        "mood": "chill",
        "tags": ["hip-hop", "jazz", "chill"],
        "source": "manual"
    },
    {
        "title": "Donuts",
        "artist": "J Dilla",
        "album": "Donuts",
        "mood": "chill",
        "tags": ["hip-hop", "beats", "instrumental"],
        "source": "manual"
    },
    {
        "title": "Time: The Donut of the Heart",
        "artist": "J Dilla",
        "album": "Donuts",
        "mood": "chill",
        "tags": ["hip-hop", "beats", "chill"],
        "source": "manual"
    },
]


def seed_tracks(count: int = None):
    """
    Seed database with sample tracks.

    Args:
        count: Number of tracks to insert (None = all samples + duplicates)
    """
    logger.info("Connecting to database...")
    db.connect()
    tracks_collection = db.get_tracks_collection()

    if count is None:
        count = len(SAMPLE_TRACKS) * 3  # Insert each track multiple times

    inserted_count = 0
    now = datetime.utcnow()

    logger.info(f"Inserting {count} sample tracks...")

    for i in range(count):
        # Pick a random track from samples
        track = random.choice(SAMPLE_TRACKS).copy()

        # Random timestamp in last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        track_time = now - timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )

        track["playedAt"] = track_time
        track["createdAt"] = track_time
        track["updatedAt"] = track_time

        # Insert into database
        result = tracks_collection.insert_one(track)
        inserted_count += 1

        if inserted_count % 10 == 0:
            logger.info(f"Inserted {inserted_count}/{count} tracks...")

    logger.info(f"✓ Successfully seeded {inserted_count} tracks!")

    # Show statistics
    total = tracks_collection.count_documents({})
    mood_counts = {}
    for mood in ['focus', 'energetic', 'chill', 'melancholic', 'happy']:
        count = tracks_collection.count_documents({"mood": mood})
        mood_counts[mood] = count

    logger.info("\nDatabase statistics:")
    logger.info(f"  Total tracks: {total}")
    logger.info("  Mood distribution:")
    for mood, count in mood_counts.items():
        logger.info(f"    {mood}: {count}")

    # Show top artists
    pipeline = [
        {"$group": {"_id": "$artist", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_artists = list(tracks_collection.aggregate(pipeline))

    logger.info("\n  Top 5 artists:")
    for artist_stat in top_artists:
        logger.info(f"    {artist_stat['_id']}: {artist_stat['count']} plays")

    db.close()


if __name__ == "__main__":
    # Parse command line argument for count
    count = None
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid count: {sys.argv[1]}")
            sys.exit(1)

    seed_tracks(count)
