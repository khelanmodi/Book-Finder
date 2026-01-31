# 📚 BookFinder - Semantic Book Discovery with OSS DocumentDB

An intelligent book recommendation system powered by OpenAI embeddings and OSS DocumentDB's native vector search. Built with async Python (FastAPI + Beanie + Motor) for high-performance, non-blocking database operations.

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)](https://fastapi.tiangolo.com/)
[![DocumentDB](https://img.shields.io/badge/DocumentDB-OSS-blue)](https://github.com/documentdb/documentdb)
[![OpenAI](https://img.shields.io/badge/OpenAI-Embeddings-orange)](https://platform.openai.com/docs/guides/embeddings)
[![Beanie](https://img.shields.io/badge/Beanie-ODM-purple)](https://beanie-odm.dev/)


## Features

- **Semantic Search**: Find books using natural language descriptions ("coming of age story", "dystopian future with rebellion")
- **AI-Powered Embeddings**: Uses OpenAI's `text-embedding-3-small` model (1536-dimensional vectors)
- **OSS DocumentDB**: MongoDB-compatible document database built on PostgreSQL
- **IVF Vector Search**: Native vector indexing for high-speed similarity search
- **Async Everything**: Fully async stack (Motor + Beanie) for non-blocking database operations
- **RESTful API**: Comprehensive API with automatic OpenAPI documentation
- **Similarity Scoring**: Shows match percentages for every search result

## Architecture
```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────────────────────┐      ┌──────────────┐
│   FastAPI (Async)               │─────→│   OpenAI     │
│   - Beanie ODM                  │      │   API        │
│   - Motor Driver                │      └──────────────┘
│   - Non-blocking I/O            │       Embedding Generation
└────────┬────────────────────────┘
         │ Async MongoDB Protocol
         ↓
┌─────────────────────────────────┐
│   OSS DocumentDB (Docker)       │
│   - MongoDB-compatible API      │
│   - PostgreSQL storage          │
│   - IVF Vector Index            │
│   - Native Vector Search        │
│   - Port 10260 (TLS enabled)    │
└─────────────────────────────────┘
```

## Prerequisites

- **Python 3.11+**
- **Docker Desktop** (for OSS DocumentDB)
- **OpenAI API Key**
- **Git** (for cloning the repository)

## Quick Start
### 1. Start OSS DocumentDB Container

```bash
docker run -d \
  --name documentdb-container \
  -p 10260:10260 \
  -e DOCUMENTDB_USER=<username> \
  -e DOCUMENTDB_PASSWORD=<password> \
  documentdb:latest
```

Verify it's running:
```bash
docker ps | grep documentdb
```

### 2. Install Python Dependencies
```bash
cd "Book Finder"
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi` - Async web framework
- `motor==3.3.2` - Async MongoDB driver
- `beanie==1.24.0` - Async ODM (Object-Document Mapper)
- `openai` - OpenAI embeddings API
- `uvicorn` - ASGI server

### 3. Configure Environment

Create a `.env` file:

```env
# OSS DocumentDB Connection
MONGODB_URL=mongodb://<username>:<password>@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true
DB_NAME=bookfinder

# OpenAI Configuration
OPENAI_KEY=sk-proj-your-openai-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# Application Settings
APP_NAME=BookFinder API
VERSION=1.0.0
DEBUG=True
ALLOWED_ORIGINS=["*"]
API_V1_PREFIX=/api/v1
```

### 4. Import Sample Books

```bash
python scripts/import_books.py books.json
```

This will:
- Import 50 classic books
- Generate OpenAI embeddings for each book (1536 dimensions)
- Store in DocumentDB with 100% embedding coverage

### 5. Create Vector Index

```bash
python scripts/create_vector_index.py
```

This creates an **IVF (Inverted File) vector index** on the `embedding` field for fast similarity search.

### 6. Start the Application

```bash
python run.py
```

You should see:
```
INFO: Starting up BookFinder API...
INFO: Connected to DocumentDB: bookfinder
INFO: Database connected successfully
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 7. Access the Application

**Web Interface** (Recommended):
- Open your browser to http://localhost:8000
- Try searching: "romance set in Victorian England"
- Explore the beautiful UI with similarity scores!

**API Testing:**

Health Check:
```bash
curl http://localhost:8000/ping
curl http://localhost:8000/api/v1/health/
```

Get Books:
```bash
curl "http://localhost:8000/api/v1/books/?limit=5"
```

Semantic Search:
```bash
curl -X POST "http://localhost:8000/api/v1/books/search/text" \
  -H "Content-Type: application/json" \
  -d '{"query": "fantasy adventure", "limit": 5}'
```

**Interactive API Docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🌐 Web Interface

Access the beautiful, responsive web interface at http://localhost:8000

![BookFinder Web Interface - Semantic Book Search](/docs/images/bookfinder-web-interface.png)

**Features:**
- 🔍 **Natural Language Search**: Type queries like "romance set in Victorian England" or "dystopian future"
- 📊 **Similarity Scores**: See how closely each book matches your query (percentage-based)
- 🎨 **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- ⚡ **Real-time Results**: Powered by async backend for instant responses
- 💡 **Smart Suggestions**: Click example searches to get started

**Example Searches:**
- "coming of age story" → Returns books like "The Catcher in the Rye", "To Kill a Mockingbird"
- "dystopian future" → Returns "1984", "Brave New World"
- "magical adventure" → Returns "The Lord of the Rings", "Harry Potter"
- "Victorian romance" → Returns "Jane Eyre", "Pride and Prejudice"
- "Philosophy & morality" → Returns "Crime and Punishment", "The Brothers Karamazov"

The web interface uses the same vector search API under the hood, providing a user-friendly way to explore your book collection semantically!

## 🎯 API Endpoints

### Books Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/books/` | Create a new book with auto-generated embedding |
| `GET` | `/api/v1/books/` | List books (supports filtering, pagination) |
| `GET` | `/api/v1/books/{id}` | Get a specific book by ID |
| `PATCH` | `/api/v1/books/{id}` | Update a book (regenerates embedding if title/description changed) |
| `DELETE` | `/api/v1/books/{id}` | Delete a book |

### Vector Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/books/search/text` | Semantic search by natural language query |
| `POST` | `/api/v1/books/{id}/similar` | Find books similar to a given book |
| `GET` | `/api/v1/books/stats/embeddings` | Get embedding coverage statistics |

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ping` | Simple health check (no database) |
| `GET` | `/api/v1/health/` | Full health check (includes database ping) |

## 📁 Project Structure

```
Book Finder/
├── app/
│   ├── main.py                      # FastAPI app with async lifespan
│   ├── config.py                    # Settings (loads from .env)
│   │
│   ├── api/v1/
│   │   ├── routes/
│   │   │   ├── health.py           # Health check endpoints
│   │   │   └── books.py            # Book CRUD + search endpoints
│   │   └── schemas/
│   │       └── book.py             # Pydantic request/response models
│   │
│   ├── core/
│   │   ├── database.py             # Async DB connection (Motor + Beanie)
│   │   └── exceptions.py           # Custom exception handlers
│   │
│   ├── models/
│   │   └── book.py                 # Beanie Document model
│   │
│   └── services/
│       ├── book_service.py         # Async book CRUD operations
│       ├── similarity_service.py   # Async vector search
│       └── embedding_service.py    # OpenAI embedding generation
│
├── static/                          # Frontend HTML/CSS/JS
├── scripts/
│   ├── import_books.py             # Import books from JSON
│   └── create_vector_index.py     # Create IVF vector index
│
├── books.json                       # Sample book data
├── requirements.txt                 # Python dependencies
├── run.py                          # Application entry point
├── .env                            # Environment configuration
└── README.md                       # This file
```

## 🔍 How It Works

### 1. **Embedding Generation**

When a book is added:
```python
# User submits book
{
  "title": "1984",
  "author": "George Orwell",
  "description": "In a terrifying dystopian future..."
}

# System generates embedding
embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input="1984. In a terrifying dystopian future..."
)

# Stores 1536-dimensional vector
book.embedding = [0.023, -0.145, 0.892, ...]  # 1536 floats
```

### 2. **Vector Search Pipeline**

```python
# User searches: "dystopian future"
query_embedding = openai.embeddings.create(...)

# DocumentDB executes vector search using IVF index
results = await Book.aggregate([
    {
        "$search": {
            "cosmosSearch": {
                "path": "embedding",
                "vector": query_embedding,
                "k": 10,
                "lSearch": 100
            }
        }
    },
    {
        "$project": {
            "title": 1,
            "author": 1,
            "similarityScore": {"$meta": "searchScore"}
        }
    }
]).to_list()

# Returns books ranked by cosine similarity
# [
#   {"title": "1984", "similarity": 0.89},
#   {"title": "Brave New World", "similarity": 0.84},
#   ...
# ]
```


## 📊 Database Schema

**Collection:** `books`
```javascript
{
  "_id": ObjectId("697da4702f5baa8c40dda976"),
  "title": "Sapiens",
  "author": "Yuval Noah Harari",
  "description": "Human history from cognitive revolution to today.",
  "genre": null,
  "isbn": null,
  "publishYear": null,
  "publisher": null,
  "pageCount": null,
  "language": "English",
  "embedding": [0.023, -0.145, 0.892, ...],  // 1536 dimensions
  "addedAt": ISODate("2026-01-31T06:42:56.162Z"),
  "createdAt": ISODate("2026-01-31T06:42:56.162Z"),
  "updatedAt": ISODate("2026-01-31T06:42:56.162Z")
}
```

**Indexes:**
```javascript
// IVF Vector Index (for similarity search)
{
  "name": "vector_index",
  "key": { "embedding": "cosmosSearch" },
  "cosmosSearchOptions": {
    "kind": "vector-ivf",
    "dimensions": 1536,
    "similarity": "COS",
    "numLists": 100
  }
}

// Text Indexes
db.books.createIndex({ "title": "text", "author": "text" })
db.books.createIndex({ "author": 1 })
db.books.createIndex({ "genre": 1 })
db.books.createIndex({ "addedAt": -1 })
```

## 🔧 Configuration Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URL` | OSS DocumentDB connection string | - | Yes |
| `DB_NAME` | Database name | `bookfinder` | No |
| `OPENAI_KEY` | OpenAI API key | - | Yes |
| `EMBEDDING_MODEL` | OpenAI embedding model | `text-embedding-3-small` | No |
| `EMBEDDING_DIM` | Vector dimensions | `1536` | No |
| `APP_NAME` | Application name | `BookFinder API` | No |
| `VERSION` | API version | `1.0.0` | No |
| `DEBUG` | Debug mode | `False` | No |
| `ALLOWED_ORIGINS` | CORS origins | `["*"]` | No |
| `API_V1_PREFIX` | API path prefix | `/api/v1` | No |

## 🧪 Usage Examples

### Example 1: Add a New Book

```bash
curl -X POST "http://localhost:8000/api/v1/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "description": "A reluctant hobbit joins dwarves to reclaim treasure from a dragon.",
    "genre": "Fantasy",
    "publishYear": 1937
  }'
```

**Response:**
```json
{
  "_id": "697db57b173c650888042989",
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "description": "A reluctant hobbit joins dwarves to reclaim treasure from a dragon.",
  "genre": "Fantasy",
  "publishYear": 1937,
  "language": "English",
  "addedAt": "2026-01-31T07:55:38.219688"
}
```

The embedding is automatically generated but not returned (too large for response).

### Example 2: Semantic Search

```bash
curl -X POST "http://localhost:8000/api/v1/books/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "magical adventure with dragons and wizards",
    "limit": 3
  }'
```

**Response:**
```json
{
  "query": "magical adventure with dragons and wizards",
  "similar_books": [
    {
      "book_id": "697da4642f5baa8c40dda94b",
      "similarity_score": 0.87,
      "book": {
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "description": "An epic quest to destroy a corrupting ring..."
      }
    },
    {
      "book_id": "697da4652f5baa8c40dda94d",
      "similarity_score": 0.84,
      "book": {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "description": "A reluctant hobbit joins dwarves..."
      }
    }
  ]
}
```

### Example 3: Find Similar Books

```bash
# Get similar books to "Sapiens" (ID: 697da4702f5baa8c40dda976)
curl -X POST "http://localhost:8000/api/v1/books/697da4702f5baa8c40dda976/similar?limit=3"
```

### Example 4: Filter Books by Author

```bash
curl "http://localhost:8000/api/v1/books/?author=Tolkien&limit=10"
```

### Example 5: Get Embedding Statistics

```bash
curl "http://localhost:8000/api/v1/books/stats/embeddings"
```

**Response:**
```json
{
  "total_books": 51,
  "books_with_embeddings": 51,
  "books_without_embeddings": 0,
  "coverage_percentage": 100.0
}
```

## 🛠️ Development Tools

### VS Code DocumentDB Extension

View and manage your DocumentDB data directly in VS Code with the official Azure DocumentDB extension.

**Install the Extension:**
- [Azure DocumentDB Extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb)

**Installation Steps:**

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Azure DocumentDB"
4. Click Install on `ms-azuretools.vscode-documentdb`

**Connect to Your Local DocumentDB:**

1. Click the DocumentDB icon in the VS Code sidebar
2. Click "+" to add a new connection
3. Select "DocumentDB Connection"
4. Enter connection string:
   ```
   mongodb://<username>:<password>@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true
   ```
5. Name your connection (e.g., "Local DocumentDB")

**Features:**

- ✅ **Browse Collections**: View the `bookfinder` database and `books` collection
- ✅ **Query Documents**: Run MongoDB queries directly in VS Code
- ✅ **View Data**: See book documents with all fields including embeddings
- ✅ **Manage Indexes**: View and manage vector indexes
- ✅ **Table View**: Browse books in a spreadsheet-like interface (as shown below)
- ✅ **Edit Documents**: Modify book data inline
- ✅ **Export/Import**: Backup and restore your data

**Example: Viewing Books Collection**

![DocumentDB Extension showing books collection with embeddings](/docs/images/documentdb-vscode-extension.png)


The extension provides a powerful GUI for:
- Inspecting book documents with their 1536-dimensional embeddings
- Viewing all 50+ books in a table format
- Filtering and sorting by author, title, or any field
- Checking embedding coverage and data integrity
- Running aggregation queries for analytics

This is especially useful during development to:
- Verify books were imported correctly
- Check that embeddings were generated (all should show `array[1536]`)
- Inspect similarity search results
- Debug data issues without using the command line

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `[Errno 10048] error while attempting to bind on address`

**Solution:**
```bash
# Find process using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill //F //PID <PID>
```

### DocumentDB Connection Failed

**Error:** `ServerSelectionTimeoutError`

**Solutions:**
1. Verify DocumentDB container is running:
   ```bash
   docker ps | grep documentdb
   ```

2. Check credentials in `.env` file match container environment variables

3. Ensure TLS settings in connection string:
   ```
   mongodb://user:pass@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true
   ```

### Requests Hanging

This was the original issue we solved! If requests hang, it means:

❌ **Using synchronous PyMongo** (blocks the async event loop)

✅ **Solution**: We migrated to **Motor + Beanie** for fully async operations

Make sure all service methods use `async def` and `await`:

```python
# ❌ WRONG (synchronous - causes hanging)
def get_books(self):
    return books_collection.find().to_list()

# ✅ CORRECT (async - non-blocking)
async def get_books(self):
    return await Book.find().to_list()
```

### OpenAI API Errors

**Error:** `AuthenticationError` or `RateLimitError`

## 🚀 Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t bookfinder-api .
docker run -p 8000:8000 --env-file .env bookfinder-api
```

## 📄 License

This project is for educational and demonstration purposes.
