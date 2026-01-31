"""File upload and storage handler."""
import os
import aiofiles
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file uploads and storage."""

    UPLOAD_DIR = Path(settings.UPLOAD_DIR)
    MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE

    def __init__(self):
        """Initialize file handler and ensure upload directory exists."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"File upload directory: {self.UPLOAD_DIR.absolute()}")

    async def save_upload(
        self,
        file: UploadFile,
        temp: bool = False
    ) -> str:
        """
        Save uploaded file to disk.

        Args:
            file: FastAPI UploadFile object
            temp: If True, save to temp location (for similarity search without storing)

        Returns:
            Absolute path to saved file

        Raises:
            ValueError: If file validation fails
        """
        # Validate file
        self._validate_file(file)

        if temp:
            # Save to temp directory
            save_dir = self.UPLOAD_DIR / "temp"
            save_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().timestamp()
            filename = f"temp_{timestamp}_{file.filename}"
        else:
            # Organize by year/month for permanent storage
            now = datetime.now()
            save_dir = self.UPLOAD_DIR / str(now.year) / f"{now.month:02d}"
            save_dir.mkdir(parents=True, exist_ok=True)

            # Create unique filename with timestamp
            timestamp = int(datetime.now().timestamp() * 1000)
            # Clean filename (remove special chars, keep extension)
            clean_name = self._clean_filename(file.filename)
            filename = f"{timestamp}_{clean_name}"

        file_path = save_dir / filename

        # Save file asynchronously
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            logger.info(f"Saved file: {file_path} ({len(content)} bytes)")
            return str(file_path)

        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            raise

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from disk.

        Args:
            file_path: Absolute path to file

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def cleanup_temp_files(self, max_age_seconds: int = 3600) -> int:
        """
        Delete temporary files older than specified age.

        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)

        Returns:
            Number of files deleted
        """
        temp_dir = self.UPLOAD_DIR / "temp"
        if not temp_dir.exists():
            return 0

        deleted_count = 0
        current_time = datetime.now().timestamp()

        try:
            for file in temp_dir.iterdir():
                if not file.is_file():
                    continue

                file_age = current_time - file.stat().st_mtime
                if file_age > max_age_seconds:
                    file.unlink()
                    deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} temporary files")

            return deleted_count

        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
            return deleted_count

    def _validate_file(self, file: UploadFile):
        """
        Validate uploaded file.

        Args:
            file: FastAPI UploadFile object

        Raises:
            ValueError: If validation fails
        """
        # Check filename
        if not file.filename:
            raise ValueError("No filename provided")

        # Check file extension
        allowed_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise ValueError(
                f"Invalid file type: {file_ext}. "
                f"Allowed types: {', '.join(allowed_extensions)}"
            )

    @staticmethod
    def _clean_filename(filename: str) -> str:
        """
        Clean filename by removing special characters.

        Args:
            filename: Original filename

        Returns:
            Cleaned filename
        """
        # Keep alphanumeric, dots, hyphens, underscores
        path = Path(filename)
        name = path.stem
        ext = path.suffix

        # Replace spaces and special chars with underscores
        cleaned_name = "".join(
            c if c.isalnum() or c in "._- " else "_"
            for c in name
        )

        # Remove multiple consecutive underscores
        while "__" in cleaned_name:
            cleaned_name = cleaned_name.replace("__", "_")

        # Trim to reasonable length (keep extension separate)
        max_name_length = 100
        if len(cleaned_name) > max_name_length:
            cleaned_name = cleaned_name[:max_name_length]

        return cleaned_name + ext

    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            File size in bytes
        """
        try:
            return Path(file_path).stat().st_size
        except Exception as e:
            logger.error(f"Failed to get file size for {file_path}: {e}")
            return 0
