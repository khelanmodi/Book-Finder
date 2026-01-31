"""Statistics and aggregation service."""
from datetime import datetime
from typing import List, Dict
import logging
from app.core.database import db

logger = logging.getLogger(__name__)


class StatsService:
    """Aggregation and statistics queries."""

    def get_top_artists_this_month(self, limit: int = 5) -> Dict:
        """
        Get top artists for the current month by play count.

        Uses MongoDB aggregation pipeline to:
        1. Filter tracks played in the current month
        2. Group by artist and count plays
        3. Sort by play count descending
        4. Limit to top N

        Args:
            limit: Number of top artists to return

        Returns:
            Dictionary with:
            - range: {from: datetime, to: datetime}
            - topArtists: [{artist: str, play_count: int, sample_tracks: [str]}]
        """
        # Calculate date range for current month
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        # Calculate next month's first day (end of range)
        if now.month == 12:
            month_end = datetime(now.year + 1, 1, 1)
        else:
            month_end = datetime(now.year, now.month + 1, 1)

        # MongoDB aggregation pipeline
        pipeline = [
            # Stage 1: Filter by date range
            {
                "$match": {
                    "playedAt": {
                        "$gte": month_start,
                        "$lt": month_end
                    }
                }
            },
            # Stage 2: Group by artist
            {
                "$group": {
                    "_id": "$artist",
                    "play_count": {"$sum": 1},
                    "tracks": {"$push": "$title"}
                }
            },
            # Stage 3: Sort by play count (descending)
            {
                "$sort": {"play_count": -1}
            },
            # Stage 4: Limit results
            {
                "$limit": limit
            },
            # Stage 5: Reshape output
            {
                "$project": {
                    "artist": "$_id",
                    "play_count": 1,
                    "sample_tracks": {"$slice": ["$tracks", 3]},  # First 3 tracks
                    "_id": 0
                }
            }
        ]

        # Execute aggregation
        tracks_collection = db.get_tracks_collection()
        results = list(tracks_collection.aggregate(pipeline))

        logger.info(
            f"Retrieved top {len(results)} artists for {month_start.strftime('%B %Y')} "
            f"(date range: {month_start} to {month_end})"
        )

        return {
            "range": {
                "from": month_start.isoformat(),
                "to": now.isoformat()
            },
            "topArtists": results
        }

    def get_mood_distribution(self) -> List[Dict]:
        """
        Get distribution of moods across all tracks.

        Returns:
            List of dicts with {mood: str, count: int, percentage: float}
        """
        tracks_collection = db.get_tracks_collection()

        pipeline = [
            {
                "$group": {
                    "_id": "$mood",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]

        results = list(tracks_collection.aggregate(pipeline))

        # Calculate total for percentages
        total = sum(r['count'] for r in results)

        distribution = [
            {
                "mood": r['_id'] if r['_id'] else "unspecified",
                "count": r['count'],
                "percentage": round((r['count'] / total * 100) if total > 0 else 0, 2)
            }
            for r in results
        ]

        logger.info(f"Mood distribution: {len(distribution)} moods, {total} total tracks")

        return distribution

    def get_listening_stats(self) -> Dict:
        """
        Get overall listening statistics.

        Returns:
            Dictionary with:
            - total_tracks: Total number of tracks
            - unique_artists: Number of unique artists
            - unique_albums: Number of unique albums
            - total_duration: Total duration in seconds (for tracks with duration)
            - average_duration: Average track duration
        """
        tracks_collection = db.get_tracks_collection()

        # Get total tracks
        total_tracks = tracks_collection.count_documents({})

        # Get unique counts
        unique_artists = len(tracks_collection.distinct("artist"))
        unique_albums = len(tracks_collection.distinct("album"))

        # Calculate duration stats
        duration_pipeline = [
            {
                "$match": {
                    "duration": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_duration": {"$sum": "$duration"},
                    "count": {"$sum": 1}
                }
            }
        ]

        duration_results = list(tracks_collection.aggregate(duration_pipeline))

        if duration_results:
            total_duration = duration_results[0]['total_duration']
            duration_count = duration_results[0]['count']
            average_duration = total_duration / duration_count if duration_count > 0 else 0
        else:
            total_duration = 0
            average_duration = 0

        logger.info(
            f"Listening stats: {total_tracks} tracks, "
            f"{unique_artists} artists, {unique_albums} albums"
        )

        return {
            "total_tracks": total_tracks,
            "unique_artists": unique_artists,
            "unique_albums": unique_albums,
            "total_duration_seconds": round(total_duration, 2),
            "average_duration_seconds": round(average_duration, 2),
            "total_duration_hours": round(total_duration / 3600, 2)
        }
