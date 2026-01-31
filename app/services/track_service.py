"""Track service for CRUD operations and filtering."""
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
import logging
from app.core.database import db
from app.models.track import Track

logger = logging.getLogger(__name__)


class TrackService:
    """Business logic for track operations."""

    def create_track(self, track_data: Dict) -> Dict:
        """
        Create a new track in the database.

        Args:
            track_data: Dictionary with track fields

        Returns:
            Created track document with _id

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        required_fields = ['title', 'artist']
        for field in required_fields:
            if field not in track_data or not track_data[field]:
                raise ValueError(f"Missing required field: {field}")

        # Set defaults
        now = datetime.utcnow()
        track_data.setdefault('playedAt', now)
        track_data.setdefault('createdAt', now)
        track_data.setdefault('updatedAt', now)
        track_data.setdefault('source', 'manual')
        track_data.setdefault('tags', [])

        # Convert playedAt to datetime if it's a string
        if isinstance(track_data.get('playedAt'), str):
            try:
                track_data['playedAt'] = datetime.fromisoformat(
                    track_data['playedAt'].replace('Z', '+00:00')
                )
            except Exception as e:
                logger.warning(f"Failed to parse playedAt: {e}, using current time")
                track_data['playedAt'] = now

        # Insert into database
        tracks_collection = db.get_tracks_collection()
        result = tracks_collection.insert_one(track_data)

        # Fetch the created document
        created_track = tracks_collection.find_one({"_id": result.inserted_id})

        logger.info(
            f"Created track: {created_track['title']} by {created_track['artist']} "
            f"(ID: {result.inserted_id}, mood: {created_track.get('mood')})"
        )

        return self._serialize_track(created_track)

    def get_track_by_id(self, track_id: str) -> Optional[Dict]:
        """
        Get a track by ID.

        Args:
            track_id: MongoDB ObjectId as string

        Returns:
            Track document or None if not found
        """
        tracks_collection = db.get_tracks_collection()

        try:
            track = tracks_collection.find_one({"_id": ObjectId(track_id)})
            if track:
                return self._serialize_track(track)
            return None
        except Exception as e:
            logger.error(f"Error fetching track {track_id}: {e}")
            return None

    def get_tracks(
        self,
        mood: Optional[str] = None,
        artist: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict]:
        """
        Get tracks with optional filtering.

        Args:
            mood: Filter by mood
            artist: Filter by artist (case-insensitive partial match)
            limit: Maximum number of results
            skip: Number of results to skip (pagination)

        Returns:
            List of track documents
        """
        tracks_collection = db.get_tracks_collection()

        # Build query
        query = {}
        if mood:
            query['mood'] = mood
        if artist:
            # Case-insensitive regex search
            query['artist'] = {"$regex": artist, "$options": "i"}

        # Execute query with sorting
        cursor = tracks_collection.find(query).sort("playedAt", -1).skip(skip).limit(limit)
        tracks = list(cursor)

        logger.info(
            f"Retrieved {len(tracks)} tracks "
            f"(mood={mood}, artist={artist}, limit={limit}, skip={skip})"
        )

        return [self._serialize_track(track) for track in tracks]

    def update_track(self, track_id: str, update_data: Dict) -> Optional[Dict]:
        """
        Update a track.

        Args:
            track_id: MongoDB ObjectId as string
            update_data: Fields to update

        Returns:
            Updated track document or None if not found
        """
        tracks_collection = db.get_tracks_collection()

        # Add updatedAt timestamp
        update_data['updatedAt'] = datetime.utcnow()

        try:
            result = tracks_collection.update_one(
                {"_id": ObjectId(track_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                updated_track = tracks_collection.find_one({"_id": ObjectId(track_id)})
                logger.info(f"Updated track: {track_id}")
                return self._serialize_track(updated_track)

            return None

        except Exception as e:
            logger.error(f"Error updating track {track_id}: {e}")
            return None

    def delete_track(self, track_id: str) -> bool:
        """
        Delete a track.

        Args:
            track_id: MongoDB ObjectId as string

        Returns:
            True if deleted, False otherwise
        """
        tracks_collection = db.get_tracks_collection()

        try:
            result = tracks_collection.delete_one({"_id": ObjectId(track_id)})
            if result.deleted_count > 0:
                logger.info(f"Deleted track: {track_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting track {track_id}: {e}")
            return False

    def get_track_count(self, mood: Optional[str] = None) -> int:
        """
        Get count of tracks, optionally filtered by mood.

        Args:
            mood: Filter by mood

        Returns:
            Number of tracks
        """
        tracks_collection = db.get_tracks_collection()
        query = {"mood": mood} if mood else {}
        return tracks_collection.count_documents(query)

    @staticmethod
    def _serialize_track(track: Dict) -> Dict:
        """
        Serialize track document for JSON response.

        Args:
            track: MongoDB track document

        Returns:
            Serialized track with _id as string
        """
        if track and '_id' in track:
            track['_id'] = str(track['_id'])

        return track
