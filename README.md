# 🌱 Eco-Friendliness Scoring Backend

A comprehensive LLM-powered backend system that evaluates product eco-friendliness using Google Gemini AI and LangGraph workflows, with MongoDB for data persistence.

## 🎯 Features

- **AI-Powered Analysis**: Uses Google Gemini API for intelligent product eco-scoring
- **LangGraph Workflows**: Structured analysis pipeline with state management
- **MongoDB Integration**: Scalable document storage with intelligent caching
- **FastAPI REST API**: Production-ready endpoints with automatic documentation
- **Comprehensive Scoring**: Evaluates carbon footprint, recyclability, sustainability, and environmental impact
- **Alternative Discovery**: Suggests eco-friendly alternatives to analyzed products
- **Batch Processing**: Concurrent analysis of multiple products
- **Performance Monitoring**: Built-in analytics and request tracking

## 🏗 Architecture

```mermaid
graph TB
    A[Client Request] --> B[FastAPI Backend]
    B --> C[LangGraph Workflow]
    C --> D[Input Validation]
    D --> E[MongoDB Cache Check]
    E --> F{Product Exists?}
    F -->|Yes| G[Return Cached Result]
    F -->|No| H[Gemini API Analysis]
    H --> I[Eco-Score Generation]
    I --> J[Category Classification]
    J --> K[Alternative Discovery]
    K --> L[Save to MongoDB]
    L --> M[Return Results]
    G --> M
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- Google Gemini API key

### Setup

1. **Clone and navigate to the project:**
```powershell
cd eco-backend
```

2. **Run the setup script:**
```powershell
# Make sure execution policy allows scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\setup.ps1
```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Add your Google Gemini API key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=eco_products
```

4. **Activate virtual environment:**
```powershell
.\venv\Scripts\Activate.ps1
```

### Testing the System

Run the comprehensive test suite:

```powershell
python src/test_workflow.py
```

This will:
- Test individual product analysis
- Test batch processing
- Verify database operations
- Check error handling
- Measure performance

### Starting the API Server

```powershell
python src/api.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Core Analysis

#### `POST /analyze`
Analyze a single product's eco-friendliness.

```json
{
  "product_name": "iPhone 15"
}
```

**Response:**
```json
{
  "success": true,
  "product_name": "iPhone 15",
  "category": "Electronics & Technology",
  "eco_score": {
    "overall_score": 65.5,
    "carbon_footprint": 60.0,
    "recyclability": 70.0,
    "sustainability": 65.0,
    "environmental_impact": 68.0,
    "reasoning": "Detailed analysis of environmental impact..."
  },
  "alternatives": [
    {
      "name": "Fairphone 5",
      "eco_score": 85.0,
      "features": ["Modular design", "Fair trade"],
      "brand": "Fairphone",
      "availability": "Online, Europe"
    }
  ],
  "from_cache": false,
  "processing_time_ms": 3500
}
```

#### `POST /analyze/batch`
Analyze multiple products concurrently (up to 10).

```json
{
  "product_names": ["iPhone 15", "Tesla Model 3", "Patagonia Jacket"]
}
```

### Database Queries

#### `GET /search`
Search existing analyzed products.

```
GET /search?query=phone&limit=20
```

#### `GET /alternatives`
Find eco-friendly alternatives above a score threshold.

```
GET /alternatives?min_score=70&category=Electronics%20%26%20Technology&limit=10
```

### System Information

#### `GET /health`
Health check endpoint.

#### `GET /statistics`
Get system usage statistics.

#### `GET /categories`
List available product categories.

## 🧪 Testing

### Manual Testing

```powershell
# Test single product
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Tesla Model 3"}'

# Test batch analysis
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{"product_names": ["iPhone 15", "Samsung Galaxy S24"]}'

# Search products
curl "http://localhost:8000/search?query=phone&limit=5"

# Get alternatives
curl "http://localhost:8000/alternatives?min_score=70&limit=5"
```

### Automated Testing

Run the comprehensive test suite:

```powershell
python src/test_workflow.py
```

Expected output:
```
🌱 Eco-Friendliness Scoring System - Test Suite
============================================================

🔧 Setting up test environment...
✅ Test environment ready!

🔍 Testing product: iPhone 15
✅ Analysis successful! (3241ms)
   Product: iPhone 15
   Category: Electronics & Technology
   Eco Score: 65.5/100
   From Cache: False
   Alternatives: 4
   Top alternatives:
   1. Fairphone 5 (Score: 85.0)
   2. Framework Laptop (Score: 82.0)
   3. refurbished iPhone 13 (Score: 78.0)

...

📋 Test Summary:
==================================================
Total tests run: 12
Successful: 11
Failed: 1
Success rate: 91.7%
Average response time: 2847ms

Category distribution:
  Electronics & Technology: 4
  Transportation: 2
  Personal Care & Beauty: 2
  Clothing & Textiles: 1
  Food & Beverages: 1
==================================================

🎉 All tests completed!
```

## 🗄 Database Schema

### ProductDocument
```javascript
{
  "_id": ObjectId,
  "name": "iPhone 15",
  "category": "Electronics & Technology",
  "eco_score": {
    "overall_score": 65.5,
    "carbon_footprint": 60.0,
    "recyclability": 70.0,
    "sustainability": 65.0,
    "environmental_impact": 68.0,
    "reasoning": "Detailed analysis..."
  },
  "alternatives": [
    {
      "name": "Fairphone 5",
      "eco_score": 85.0,
      "features": ["Modular", "Fair trade"],
      "brand": "Fairphone",
      "comparison": "More sustainable alternative",
      "availability": "Online, Europe"
    }
  ],
  "brand": "Apple",
  "features": ["Premium build", "Long support"],
  "tags": ["smartphone", "electronics", "apple"],
  "created_at": ISODate,
  "updated_at": ISODate,
  "analysis_version": "1.0",
  "confidence_score": 0.85
}
```

### AnalysisHistoryDocument
```javascript
{
  "_id": ObjectId,
  "product_name": "iPhone 15",
  "request_timestamp": ISODate,
  "processing_time_ms": 3241,
  "success": true,
  "error_message": null,
  "user_agent": "curl/7.68.0",
  "ip_address": "127.0.0.1"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | Required |
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `eco_products` |
| `HOST` | API host | `0.0.0.0` |
| `PORT` | API port | `8000` |
| `DEBUG` | Debug mode | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |

### MongoDB Setup

#### Local MongoDB
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data/directory
```

#### MongoDB Atlas (Cloud)
1. Create account at mongodb.com/atlas
2. Create cluster
3. Get connection string
4. Update `MONGODB_URL` in `.env`

## 🔍 Monitoring & Logging

The system includes comprehensive logging and monitoring:

- **Request/Response Logging**: All API calls are logged with timing
- **Error Tracking**: Detailed error logging with stack traces
- **Performance Metrics**: Processing time tracking and statistics
- **Database Analytics**: Request success rates and usage patterns

View logs in real-time:
```powershell
# API logs
tail -f logs/api.log

# System logs  
tail -f logs/system.log
```

## 🚀 Production Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000
CMD ["python", "src/api.py"]
```

### Environment Setup

```bash
# Production environment variables
GOOGLE_API_KEY=your_production_key
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=eco_products_prod
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000
```

### Security Considerations

- **API Keys**: Use environment variables, never commit to code
- **CORS**: Configure allowed origins for production
- **Rate Limiting**: Implement request rate limiting
- **Authentication**: Add API key authentication for production use
- **HTTPS**: Use SSL/TLS encryption
- **Database Security**: Use MongoDB authentication and encryption

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `python src/test_workflow.py`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [troubleshooting guide](#troubleshooting)
2. Review the logs for error messages
3. Ensure all environment variables are set correctly
4. Verify MongoDB connection
5. Test Gemini API key with a simple request

### Troubleshooting

**Common Issues:**

1. **"Service not initialized" error**
   - Check MongoDB connection
   - Verify environment variables
   - Ensure database is running

2. **Gemini API errors**
   - Verify API key is correct
   - Check rate limits
   - Ensure sufficient API quota

3. **Import errors**
   - Activate virtual environment
   - Install requirements: `pip install -r requirements.txt`

4. **Database connection issues**
   - Check MongoDB service status
   - Verify connection string
   - Test network connectivity

---

**Built with ❤️ for a more sustainable future** 🌍
