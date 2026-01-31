"""Main FastAPI application with async DocumentDB support."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import logging
from pathlib import Path

from app.config import settings
from app.core.database import db
from app.core.exceptions import (
    validation_exception_handler,
    generic_exception_handler
)

# Import routers
from app.api.v1.routes import health, books

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: startup and shutdown."""
    # Startup
    logger.info("Starting up BookFinder API...")
    try:
        await db.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    yield  # Application is running

    # Shutdown
    logger.info("Shutting down BookFinder API...")
    await db.close()
    logger.info("Database connection closed")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Book similarity search API using OpenAI embeddings with async DocumentDB",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Simple test endpoint (no database, no files)
@app.get("/ping")
async def ping():
    """Simple ping endpoint for testing."""
    return {"message": "pong", "async": True}


# Include routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(books.router, prefix=settings.API_V1_PREFIX)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Root endpoint - serve the frontend
@app.get("/")
async def root():
    """Serve the frontend application."""
    index_path = static_dir / "index.html"
    return FileResponse(index_path)
