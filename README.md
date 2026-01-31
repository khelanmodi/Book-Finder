# 📚 BookFinder - AI-Powered Book Discovery

An intelligent book recommendation system that uses OpenAI embeddings and Azure DocumentDB's native vector search to find semantically similar books based on natural language queries.

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)
![Azure](https://img.shields.io/badge/Azure-DocumentDB-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-Embeddings-orange)

## 🌟 Features

- **Semantic Search**: Find books using natural language descriptions like "coming of age story" or "dystopian future with rebellion"
- **AI-Powered Embeddings**: Uses OpenAI's `text-embedding-3-small` model to create 1536-dimensional vector representations
- **Azure Native Vector Search**: Leverages Azure DocumentDB's DiskANN algorithm for high-speed similarity search
- **Modern Web UI**: Clean, responsive interface with real-time search and similarity scores
- **RESTful API**: Comprehensive API with automatic OpenAPI documentation
- **100% Coverage**: All books automatically get embeddings when added

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐      ┌──────────────┐
│   FastAPI       │─────→│   OpenAI     │
│   Backend       │      │   API        │
└────────┬────────┘      └──────────────┘
         │                Embedding Generation
         ↓
┌─────────────────────────────────────┐
│   Azure DocumentDB                  │
│   (MongoDB API)                     │
│   - Books Collection                │
│   - DiskANN Vector Index            │
│   - Native Vector Search            │
└─────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.11 or higher
- Azure DocumentDB account
- OpenAI API key
- pip (Python package manager)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000
DB_NAME=bookfinder
OPENAI_KEY=sk-proj-your-openai-api-key
DEBUG=True
ALLOWED_ORIGINS=["*"]
```

### 3. Import Books

```bash
python scripts/import_books.py books.json
```

### 4. Create Vector Index

```bash
python scripts/create_vector_index.py
```

### 5. Start Application

```bash
python run.py
```

Visit http://localhost:8000

## 🛠️ Development Tools

### VS Code DocumentDB Extension

View and manage your Azure DocumentDB data directly in VS Code:

**Install the extension:**
- [Azure DocumentDB Extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb)

**Features:**
- Browse your DocumentDB collections
- View and edit documents
- Query data with MongoDB syntax
- Monitor database statistics
- Create and manage indexes

**Usage:**
1. Install the extension in VS Code
2. Click the Azure icon in the sidebar
3. Sign in to your Azure account
4. Browse to your DocumentDB cluster
5. Explore the `bookfinder` database and `books` collection

This makes it easy to inspect your book documents, embeddings, and verify data integrity during development.

## 🎯 Usage Examples

### Web Interface

Search queries to try:
- "coming of age story"
- "dystopian totalitarian future"
- "epic fantasy quest"
- "love and tragedy"
- "philosophical exploration of morality"

### API Examples

**Search by text:**
```bash
curl -X POST http://localhost:8000/api/v1/books/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "coming of age story", "limit": 5}'
```

**Get all books:**
```bash
curl http://localhost:8000/api/v1/books?limit=50
```

**Add a book:**
```bash
curl -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Alchemist",
    "author": "Paulo Coelho",
    "description": "A young shepherd journey to find treasure..."
  }'
```

## 📁 Project Structure

```
vibe coding/
├── app/
│   ├── api/v1/routes/        # API endpoints
│   ├── services/             # Business logic
│   ├── core/                 # Database & config
│   └── main.py              # FastAPI app
├── static/                   # Frontend files
├── scripts/                  # Utility scripts
├── books.json               # Sample data
├── requirements.txt         # Dependencies
└── run.py                   # Entry point
```

## 🔍 How It Works

1. **Embedding Generation**: OpenAI converts book title + description into 1536-dimensional vector
2. **Storage**: Vector stored in Azure DocumentDB with book metadata
3. **Search**: Query converted to embedding, DiskANN finds most similar vectors using cosine similarity
4. **Results**: Books ranked by similarity score (0-1, higher = more similar)

## 📊 Database Schema

```javascript
{
  "_id": ObjectId("..."),
  "title": "1984",
  "author": "George Orwell",
  "description": "In a terrifying dystopian future...",
  "embedding": [0.1, -0.3, 0.7, ...],  // 1536 dimensions
  "addedAt": ISODate("..."),
  // Optional fields: genre, isbn, publishYear, etc.
}
```

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | DocumentDB connection | Required |
| `OPENAI_KEY` | OpenAI API key | Required |
| `DB_NAME` | Database name | `bookfinder` |
| `EMBEDDING_MODEL` | Model name | `text-embedding-3-small` |
| `EMBEDDING_DIM` | Vector dimensions | `1536` |

## 📈 Performance

- Embedding generation: ~1-2 seconds per book
- Vector search: <100ms
- Scalability: Up to 500,000+ books

## 🐛 Troubleshooting

**Connection errors**: Check `MONGODB_URL` in `.env`

**No results**: Ensure you ran import and index creation scripts

**OpenAI errors**: Verify `OPENAI_KEY` is valid

## 🚀 Deployment

Deploy to Azure App Service:
1. Create Python 3.11 App Service
2. Set environment variables
3. Deploy code via Azure CLI or VS Code
4. Configure DocumentDB firewall rules

## 📝 API Documentation

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

