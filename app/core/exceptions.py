"""Custom exceptions and global exception handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError
import logging

logger = logging.getLogger(__name__)


# Custom Exceptions

class TrackNotFoundException(Exception):
    """Track not found in database."""
    pass


class AudioProcessingException(Exception):
    """Error processing audio file."""
    pass


class InvalidFileException(Exception):
    """Invalid file upload."""
    pass


# Global Exception Handlers

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


async def pymongo_exception_handler(request: Request, exc: PyMongoError):
    """Handle MongoDB errors."""
    logger.error(f"MongoDB error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "database_error",
            "message": "Database operation failed"
        }
    )


async def track_not_found_handler(request: Request, exc: TrackNotFoundException):
    """Handle track not found errors."""
    logger.warning(f"Track not found: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "track_not_found",
            "message": str(exc)
        }
    )


async def audio_processing_handler(request: Request, exc: AudioProcessingException):
    """Handle audio processing errors."""
    logger.error(f"Audio processing error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "audio_processing_error",
            "message": str(exc)
        }
    )


async def invalid_file_handler(request: Request, exc: InvalidFileException):
    """Handle invalid file upload errors."""
    logger.warning(f"Invalid file: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "invalid_file",
            "message": str(exc)
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred"
        }
    )
