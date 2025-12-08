# Smart Shopping Module

AI-powered shopping assistant with product recommendations, NLP processing, and multi-platform product search.

## Features

1. **Product Search** - Search products across multiple platforms (eBay, Amazon, Walmart) using official APIs
2. **NLP Query Processing** - Uses SpaCy to extract keywords and understand user intent
3. **AI Recommendations** - OpenAI-powered personalized product recommendations
4. **Currency Conversion** - Real-time currency conversion using forex-python
5. **Search History** - MongoDB-based search history management
6. **Chat Assistant** - Context-aware AI chat assistant for shopping guidance

## API Endpoints

### Search Products
```
POST /api/smart-shopping/search
Body: {
    "query": "gaming laptop",
    "filters": {
        "priceRange": [0, 1000],
        "rating": 4,
        "category": "electronics"
    },
    "currency": "USD",
    "user_id": "user123"
}
```

### Get Recommendations
```
POST /api/smart-shopping/recommendations
Body: {
    "preferences": {
        "category": "electronics",
        "keywords": ["wireless", "bluetooth"]
    },
    "budget": 500,
    "currency": "USD",
    "search_history": ["laptop", "headphones"]
}
```

### Chat Assistant
```
POST /api/smart-shopping/chat
Body: {
    "message": "What's the best budget laptop?",
    "user_id": "user123",
    "context": {}
}
```

### Search History
```
GET /api/smart-shopping/history?user_id=user123&limit=50
POST /api/smart-shopping/history (add new)
PUT /api/smart-shopping/history (update)
DELETE /api/smart-shopping/history?id=search_id (delete)
```

### Process Query (NLP)
```
POST /api/smart-shopping/process-query
Body: {
    "query": "cheap wireless headphones under $50"
}
```

### Convert Currency
```
POST /api/smart-shopping/convert-currency
Body: {
    "amount": 100,
    "from_currency": "USD",
    "to_currency": "EUR"
}
```

## Environment Variables

Add these to your `.env` file:

```env
# OpenAI API Key (for AI recommendations and chat)
OPENAI_API_KEY=your_openai_api_key

# eBay API (optional - uses mock data if not set)
EBAY_APP_ID=your_ebay_app_id

# RapidAPI Key (optional - uses mock data if not set)
RAPIDAPI_KEY=your_rapidapi_key

# MongoDB URI
MONGO_URI=mongodb://localhost:27017/smart_kitchen
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download SpaCy English model:
```bash
python -m spacy download en_core_web_sm
```

3. Set up environment variables in `.env` file

4. Run the Flask app:
```bash
python app.py
```

## Product API Integration

The module uses official APIs from:
- **eBay Finding API** - For eBay product search
- **RapidAPI** - For Amazon and Walmart product search

If API keys are not configured, the system falls back to mock data for development/testing purposes.

## Notes

- The system works without API keys using mock data
- For production, configure API keys for real product data
- MongoDB is used for search history storage
- All currency conversions use real-time rates when available

