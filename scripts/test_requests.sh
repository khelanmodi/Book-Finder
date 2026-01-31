#!/bin/bash

# Test requests for What's Playing API
# Usage: bash scripts/test_requests.sh

API_BASE="http://localhost:8000/api/v1"

echo "========================================="
echo "What's Playing API - Test Requests"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}1. Health Check${NC}"
echo "GET $API_BASE/health"
curl -s -X GET "$API_BASE/health" | python -m json.tool
echo -e "\n"

# 2. Create a Track (with mood inference)
echo -e "${BLUE}2. Create Track (with mood inference from tags)${NC}"
echo "POST $API_BASE/tracks"
TRACK_RESPONSE=$(curl -s -X POST "$API_BASE/tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lofi Study Beats",
    "artist": "ChillHop Music",
    "album": "Focus Sessions",
    "tags": ["lofi", "instrumental", "study", "chill"],
    "source": "manual"
  }')

echo "$TRACK_RESPONSE" | python -m json.tool
TRACK_ID=$(echo "$TRACK_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['_id'])" 2>/dev/null)
echo -e "\n"

# 3. Create Track with Explicit Mood
echo -e "${BLUE}3. Create Track (explicit mood)${NC}"
echo "POST $API_BASE/tracks"
curl -s -X POST "$API_BASE/tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "album": "A Night at the Opera",
    "mood": "energetic",
    "tags": ["rock", "classic"],
    "source": "manual"
  }' | python -m json.tool
echo -e "\n"

# 4. Get Tracks by Mood
echo -e "${BLUE}4. Get Tracks (filter by mood: focus)${NC}"
echo "GET $API_BASE/tracks?mood=focus&limit=5"
curl -s -X GET "$API_BASE/tracks?mood=focus&limit=5" | python -m json.tool
echo -e "\n"

# 5. Get Tracks by Artist
echo -e "${BLUE}5. Get Tracks (filter by artist: ChillHop)${NC}"
echo "GET $API_BASE/tracks?artist=ChillHop&limit=3"
curl -s -X GET "$API_BASE/tracks?artist=ChillHop&limit=3" | python -m json.tool
echo -e "\n"

# 6. Get Top Artists
echo -e "${BLUE}6. Get Top Artists (this month)${NC}"
echo "GET $API_BASE/stats/top-artists"
curl -s -X GET "$API_BASE/stats/top-artists" | python -m json.tool
echo -e "\n"

# 7. Get Mood Distribution
echo -e "${BLUE}7. Get Mood Distribution${NC}"
echo "GET $API_BASE/stats/mood-distribution"
curl -s -X GET "$API_BASE/stats/mood-distribution" | python -m json.tool
echo -e "\n"

# 8. Get Listening Stats
echo -e "${BLUE}8. Get Listening Statistics${NC}"
echo "GET $API_BASE/stats/listening"
curl -s -X GET "$API_BASE/stats/listening" | python -m json.tool
echo -e "\n"

# 9. Get Specific Track
if [ ! -z "$TRACK_ID" ]; then
  echo -e "${BLUE}9. Get Specific Track${NC}"
  echo "GET $API_BASE/tracks/$TRACK_ID"
  curl -s -X GET "$API_BASE/tracks/$TRACK_ID" | python -m json.tool
  echo -e "\n"
fi

# 10. Search Similar by Track ID
if [ ! -z "$TRACK_ID" ]; then
  echo -e "${BLUE}10. Search Similar Songs (by track ID)${NC}"
  echo "POST $API_BASE/search/similar?track_id=$TRACK_ID&limit=5"
  curl -s -X POST "$API_BASE/search/similar?track_id=$TRACK_ID&limit=5" | python -m json.tool
  echo -e "\n"
fi

# 11. Get Embedding Stats
echo -e "${BLUE}11. Get Embedding Statistics${NC}"
echo "GET $API_BASE/search/embedding-stats"
curl -s -X GET "$API_BASE/search/embedding-stats" | python -m json.tool
echo -e "\n"

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Test requests completed!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "To test file upload, use:"
echo "  curl -X POST $API_BASE/tracks/upload -F 'file=@/path/to/song.mp3'"
echo ""
echo "To search similar by audio file:"
echo "  curl -X POST $API_BASE/search/similar -F 'file=@/path/to/song.mp3'"
