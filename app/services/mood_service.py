"""Mood inference service for mapping tags to moods."""
from typing import List, Optional


class MoodService:
    """Infer mood from tags using rule-based mapping."""

    # Tag-to-mood mapping rules
    MOOD_MAPPINGS = {
        'focus': [
            'ambient', 'instrumental', 'minimal', 'lofi', 'concentration',
            'study', 'work', 'deep', 'calm', 'meditation', 'deepwork',
            'coding', 'productivity'
        ],
        'energetic': [
            'upbeat', 'dance', 'electronic', 'edm', 'workout', 'party',
            'energetic', 'fast', 'pump', 'high-energy', 'rock', 'metal',
            'trap', 'drum-and-bass', 'dnb', 'techno', 'house'
        ],
        'chill': [
            'chill', 'relaxing', 'downtempo', 'smooth', 'jazz', 'acoustic',
            'mellow', 'laid-back', 'easy', 'soft', 'lounge', 'chillout',
            'lo-fi', 'beats'
        ],
        'melancholic': [
            'sad', 'melancholic', 'emotional', 'dark', 'moody', 'introspective',
            'somber', 'melancholy', 'blue', 'nostalgic', 'reflective',
            'depressing', 'gloomy'
        ],
        'happy': [
            'happy', 'uplifting', 'cheerful', 'positive', 'joyful', 'bright',
            'feel-good', 'sunshine', 'optimistic', 'fun', 'poppy', 'pop'
        ]
    }

    def infer_mood(self, tags: List[str]) -> Optional[str]:
        """
        Infer mood from tags using priority-based matching.

        Args:
            tags: List of tag strings

        Returns:
            Mood string or None if no match
        """
        if not tags:
            return None

        # Normalize tags to lowercase
        normalized_tags = [tag.lower().strip() for tag in tags]

        # Count matches for each mood
        mood_scores = {}
        for mood, keywords in self.MOOD_MAPPINGS.items():
            score = sum(1 for keyword in keywords if keyword in normalized_tags)
            if score > 0:
                mood_scores[mood] = score

        # Return mood with highest score
        if mood_scores:
            return max(mood_scores, key=mood_scores.get)

        return None

    def get_mood_tags(self, mood: str) -> List[str]:
        """
        Get representative tags for a mood.

        Args:
            mood: Mood string

        Returns:
            List of representative tags
        """
        return self.MOOD_MAPPINGS.get(mood, [])

    @staticmethod
    def get_valid_moods() -> List[str]:
        """Get list of valid mood values."""
        return ['focus', 'energetic', 'chill', 'melancholic', 'happy']
