"""Audio processing service using librosa for feature extraction and embedding creation."""
import librosa
import numpy as np
from typing import Tuple, Dict
from pathlib import Path
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Extract audio features and create embeddings using librosa."""

    SAMPLE_RATE = settings.SAMPLE_RATE  # 22050 Hz
    EMBEDDING_DIM = settings.EMBEDDING_DIM  # 128 dimensions

    def extract_features(self, audio_path: str) -> Dict:
        """
        Extract comprehensive audio features using librosa.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with extracted features:
            - mfccs: 20 Mel-frequency cepstral coefficients (mean over time)
            - spectral_centroid: Mean spectral centroid (brightness)
            - chroma: 12 pitch class profiles (mean over time)
            - spectral_contrast: 7 spectral contrast bands (mean over time)
            - zcr: Mean zero crossing rate (percussiveness)
            - tempo: Detected tempo in BPM
            - duration: Duration in seconds
        """
        try:
            # Load audio file (mono, resampled to SAMPLE_RATE)
            y, sr = librosa.load(audio_path, sr=self.SAMPLE_RATE, mono=True)

            features = {}

            # MFCCs (Mel-frequency cepstral coefficients) - 20 coefficients
            # Captures spectral characteristics of the audio
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            features['mfccs'] = np.mean(mfccs, axis=1)  # Average over time

            # Spectral centroid (brightness of sound)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            features['spectral_centroid'] = np.mean(spectral_centroid)

            # Chroma features (pitch class profiles)
            # Represents harmonic and melodic characteristics
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma'] = np.mean(chroma, axis=1)  # 12 pitch classes

            # Spectral contrast
            # Measures difference between peaks and valleys in spectrum
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            features['spectral_contrast'] = np.mean(spectral_contrast, axis=1)

            # Zero crossing rate (percussiveness)
            zcr = librosa.feature.zero_crossing_rate(y)
            features['zcr'] = np.mean(zcr)

            # Tempo (BPM)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)

            # Duration
            features['duration'] = float(librosa.get_duration(y=y, sr=sr))

            logger.info(f"Extracted features from {audio_path}: duration={features['duration']:.2f}s, tempo={features['tempo']:.1f} BPM")

            return features

        except Exception as e:
            logger.error(f"Failed to extract features from {audio_path}: {e}")
            raise

    def create_embedding(self, features: Dict) -> np.ndarray:
        """
        Create fixed-size embedding vector from extracted features.

        Strategy:
        - MFCCs: 20 dimensions
        - Chroma: 12 dimensions
        - Spectral contrast: 7 dimensions
        - Additional features: 3 dimensions (spectral_centroid, zcr, tempo normalized)
        - Total: 42 base dimensions, padded to 128 with zeros
        - L2 normalized for cosine similarity

        Args:
            features: Dictionary of extracted features

        Returns:
            128-dimensional embedding vector (numpy array)
        """
        components = []

        # MFCCs (20 dims)
        components.append(features['mfccs'])

        # Chroma (12 dims)
        components.append(features['chroma'])

        # Spectral contrast (7 dims)
        components.append(features['spectral_contrast'])

        # Scalar features (normalized to 0-1 range)
        scalars = np.array([
            features['spectral_centroid'] / 5000.0,  # Normalize (typical range: 0-5000)
            features['zcr'],  # Already in 0-1 range
            features['tempo'] / 200.0,  # Normalize (typical range: 0-200 BPM)
        ])
        components.append(scalars)

        # Concatenate all components
        embedding = np.concatenate(components)

        # Pad or truncate to exactly EMBEDDING_DIM dimensions
        if len(embedding) < self.EMBEDDING_DIM:
            # Pad with zeros
            embedding = np.pad(embedding, (0, self.EMBEDDING_DIM - len(embedding)))
        elif len(embedding) > self.EMBEDDING_DIM:
            # Truncate (shouldn't happen with current features, but safeguard)
            embedding = embedding[:self.EMBEDDING_DIM]

        # L2 normalization for cosine similarity
        # Avoid division by zero
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        else:
            embedding = embedding / (norm + 1e-8)

        return embedding

    def process_audio_file(self, audio_path: str) -> Tuple[np.ndarray, float]:
        """
        Complete pipeline: load audio → extract features → create embedding.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (embedding vector, duration in seconds)
        """
        # Extract features
        features = self.extract_features(audio_path)

        # Create embedding
        embedding = self.create_embedding(features)

        logger.info(f"Created {self.EMBEDDING_DIM}-dim embedding for {audio_path}")

        return embedding, features['duration']

    @staticmethod
    def validate_audio_file(file_path: str) -> bool:
        """
        Validate that file exists and is a valid audio file.

        Args:
            file_path: Path to file

        Returns:
            True if valid, False otherwise
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Audio file does not exist: {file_path}")
            return False

        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
        if path.suffix.lower() not in valid_extensions:
            logger.error(f"Invalid audio file extension: {path.suffix}")
            return False

        return True
