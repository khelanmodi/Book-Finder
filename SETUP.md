# What's Playing? API - Setup Guide

Complete setup instructions to get your music logging API running locally.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.10+** installed
   ```bash
   python --version  # Should be 3.10 or higher
   ```

2. **MongoDB** running locally or accessible remotely
   - Local: [Download MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Cloud: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free tier available)
   - Azure: [Azure Cosmos DB for MongoDB](https://azure.microsoft.com/en-us/services/cosmos-db/)

3. **FFmpeg** installed (required by librosa)
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Step-by-Step Setup

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI, uvicorn (web framework)
- pymongo (MongoDB driver)
- librosa, numpy, scipy (audio processing)
- pydantic, python-dotenv (configuration)
- aiofiles (async file operations)

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
# On Windows, use: copy .env.example .env
```

Edit [.env](.env) file:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DB_NAME=whats_playing

# Application Settings
DEBUG=True
ALLOWED_ORIGINS=["http://localhost:3000"]

# File Upload Settings
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# Audio Processing Settings
SAMPLE_RATE=22050
EMBEDDING_DIM=128
```

**MongoDB Connection Strings:**

- **Local MongoDB**: `mongodb://localhost:27017`
- **MongoDB Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`
- **Azure Cosmos DB**: `mongodb://account-name:password@account-name.mongo.cosmos.azure.com:10255/?ssl=true`

### 4. Start MongoDB (if running locally)

```bash
# Create data directory
mkdir -p data

# Start MongoDB
mongod --dbpath ./data
```

Leave this terminal running and open a new one for the next steps.

### 5. Seed Sample Data (Optional but Recommended)

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run seed script (inserts ~50 sample tracks)
python scripts/seed_data.py

# Or specify a custom count
python scripts/seed_data.py 100
```

This will populate your database with sample tracks for testing.

### 6. Start the API Server

```bash
# Make sure virtual environment is activated
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting up What's Playing API...
INFO:     ✓ Database connected successfully
INFO:     Application startup complete.
```

### 7. Test the API

**Option 1: Open Swagger UI**
Open your browser and navigate to:
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Option 2: Run Test Requests**

```bash
# In a new terminal (keep the server running)
bash scripts/test_requests.sh
```

**Option 3: Manual curl Commands**

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create a track
curl -X POST http://localhost:8000/api/v1/tracks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lofi Study Beats",
    "artist": "ChillHop Music",
    "tags": ["lofi", "study", "chill"]
  }'

# Get tracks by mood
curl http://localhost:8000/api/v1/tracks?mood=focus&limit=5

# Get top artists
curl http://localhost:8000/api/v1/stats/top-artists
```

## Testing Audio Upload & Similarity Search

To test the MP3 upload and similarity search features, you'll need sample MP3 files.

### Download Sample MP3 Files

You can use royalty-free music from:
- [Free Music Archive](https://freemusicarchive.org/)
- [ccMixter](http://ccmixter.org/)
- [Incompetech](https://incompetech.com/)

### Upload an MP3

```bash
curl -X POST http://localhost:8000/api/v1/tracks/upload \
  -F "file=@/path/to/your/song.mp3" \
  -F "title=My Song" \
  -F "artist=My Artist" \
  -F "tags=lofi,chill"
```

This will:
1. Upload the MP3 file
2. Extract audio features using librosa
3. Create a 128-dim embedding
4. Save the track to the database
5. Find and return 10 similar tracks

### Search for Similar Songs

**By track ID:**
```bash
curl -X POST "http://localhost:8000/api/v1/search/similar?track_id=<track_id>&limit=5"
```

**By uploading a probe audio file:**
```bash
curl -X POST http://localhost:8000/api/v1/search/similar \
  -F "file=@/path/to/probe.mp3"
```

## Common Issues & Troubleshooting

### Issue: "Failed to connect to MongoDB"

**Solution:**
- Check MongoDB is running: `mongosh` or `mongo`
- Verify MONGODB_URL in .env matches your MongoDB instance
- For MongoDB Atlas, ensure your IP is whitelisted

### Issue: "librosa not found" or audio processing errors

**Solution:**
- Ensure FFmpeg is installed: `ffmpeg -version`
- On Windows, make sure FFmpeg is in your PATH
- Reinstall librosa: `pip install --force-reinstall librosa`

### Issue: "No module named 'app'"

**Solution:**
- Ensure you're in the project root directory
- Virtual environment is activated
- All dependencies are installed: `pip install -r requirements.txt`

### Issue: File upload fails with "File too large"

**Solution:**
- Default max size is 10MB
- Increase MAX_UPLOAD_SIZE in .env (value in bytes)
- Restart the server after changing .env

### Issue: Slow audio processing

**Solution:**
- librosa processing takes 2-5 seconds per track (normal)
- For faster processing, reduce SAMPLE_RATE in .env (e.g., 16000)
- Consider adding async processing with Celery for production

## Project Structure

```
whats-playing-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings
│   ├── api/v1/              # API routes & schemas
│   ├── core/                # Database & exceptions
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   └── utils/               # Utilities
├── scripts/
│   ├── seed_data.py         # Database seeding
│   └── test_requests.sh     # Test requests
├── uploads/                 # Uploaded audio files
├── .env                     # Configuration
├── requirements.txt         # Dependencies
└── run.py                   # Entry point
```

## Next Steps

### For Development

1. **Explore the API**: Use Swagger UI at http://localhost:8000/docs
2. **Test endpoints**: Run `bash scripts/test_requests.sh`
3. **Upload audio**: Test MP3 upload and similarity search
4. **Check stats**: View mood distribution and top artists

### For Production

1. **Use a production MongoDB instance** (MongoDB Atlas or Azure Cosmos DB)
2. **Set DEBUG=False** in .env
3. **Configure ALLOWED_ORIGINS** for CORS
4. **Add authentication** (JWT or API keys)
5. **Use cloud storage** for audio files (S3 or Azure Blob)
6. **Deploy with Docker** (see Dockerfile in README)
7. **Add monitoring** (logs, metrics, health checks)

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/tracks` | POST | Create track |
| `/api/v1/tracks` | GET | List tracks (filter by mood/artist) |
| `/api/v1/tracks/{id}` | GET | Get specific track |
| `/api/v1/tracks/{id}` | PATCH | Update track |
| `/api/v1/tracks/{id}` | DELETE | Delete track |
| `/api/v1/tracks/upload` | POST | Upload MP3 + get similar songs |
| `/api/v1/search/similar` | POST | Find similar songs (by ID or file) |
| `/api/v1/search/embedding-stats` | GET | Embedding coverage stats |
| `/api/v1/stats/top-artists` | GET | Top 5 artists this month |
| `/api/v1/stats/mood-distribution` | GET | Mood distribution |
| `/api/v1/stats/listening` | GET | Overall listening stats |

## Support

For issues or questions:
- Check the [README](README.md)
- Review the [implementation plan](.claude/plans/joyful-growing-moon.md)
- Open an issue on GitHub

---

Happy coding! 🎵🚀
