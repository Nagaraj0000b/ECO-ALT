# 🌱 Eco-Backend Quick Start

## ✅ System is Ready!

Your eco-friendliness scoring backend is now set up and working! Here's how to use it:

## 🚀 Start the API Server

1. **Open a terminal** (separate from this one)
2. **Navigate to the project**:
   ```powershell
   cd C:\Users\nagar\OneDrive\Desktop\Warp-Testing\eco-backend
   ```
3. **Activate virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. **Start the server**:
   ```powershell
   python api.py
   ```

The server will start on: **http://localhost:8000**

## 🧪 Test the System

### Option 1: Run Test Script
```powershell
python test_api.py
```

### Option 2: Manual API Testing
```bash
# Test health
curl http://localhost:8000/health

# Analyze a product
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15"}'
```

### Option 3: Interactive Documentation
Open in browser: **http://localhost:8000/docs**

## 📱 Example API Usage

**Request:**
```json
POST /analyze
{
  "product_name": "iPhone 15"
}
```

**Response:**
```json
{
  "success": true,
  "product_name": "iPhone 15",
  "category": "Smartphone",
  "eco_score": {
    "overall_score": 68.5,
    "carbon_footprint": 65.0,
    "recyclability": 75.0,
    "sustainability": 70.0,
    "environmental_impact": 70.0,
    "reasoning": "The iPhone 15 uses recycled materials..."
  },
  "alternatives": [
    {
      "name": "Fairphone 4",
      "eco_score": 82.0,
      "features": ["Modular design", "Fair trade materials"],
      "brand": "Fairphone",
      "availability": "Online, Europe"
    }
  ],
  "processing_time_ms": 3200
}
```

## 🔧 What's Working

✅ **Gemini AI Integration**: Using Google's Gemini-1.5-Flash model  
✅ **Eco-Scoring**: Multi-dimensional analysis (carbon, recyclability, sustainability)  
✅ **Alternative Discovery**: Suggests better eco-friendly products  
✅ **FastAPI Server**: Production-ready REST API  
✅ **Auto Documentation**: Swagger/OpenAPI docs  
✅ **Error Handling**: Robust error responses  
✅ **CORS Support**: Ready for web frontend integration  

## 🌟 Key Features

- **AI-Powered Analysis**: Intelligent product evaluation
- **Comprehensive Scoring**: 5 different eco-dimensions
- **Alternative Suggestions**: Better eco-friendly options
- **Fast Response**: Typically 2-4 seconds per analysis
- **JSON API**: Easy integration with any frontend
- **Auto Documentation**: Built-in API docs

## 🔗 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze` - Analyze product eco-friendliness
- `GET /test` - Simple test endpoint
- `GET /docs` - Interactive API documentation
- `GET /redoc` - ReDoc documentation

## 🎯 Next Steps

1. **Test with different products** - Try various product names
2. **Build a frontend** - Create a web interface using the API
3. **Add MongoDB** - For data persistence and caching
4. **Scale up** - Deploy to cloud for production use

## 💡 Example Products to Test

- Electronics: "iPhone 15", "Samsung Galaxy", "MacBook Pro"
- Transportation: "Tesla Model 3", "Toyota Prius", "Electric Scooter"
- Fashion: "Fast Fashion T-shirt", "Organic Cotton Jeans"
- Home: "LED Light Bulb", "Solar Panel", "Bamboo Toothbrush"

## 🛠 Troubleshooting

**API not responding?**
- Check if server is running: `python src/simple_api.py`
- Verify URL: http://localhost:8000

**Gemini API errors?**
- Check API key in `.env` file
- Verify internet connection

**Need help?**
- Check server logs in the terminal where you started the API
- Visit the documentation: http://localhost:8000/docs

---

**🎉 Your eco-scoring backend is ready to help make the world more sustainable!** 🌍
