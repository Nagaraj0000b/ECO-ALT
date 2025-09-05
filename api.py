"""
Simple FastAPI server for eco-scoring without complex dependencies.
"""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


# Pydantic models
class ProductAnalysisRequest(BaseModel):
    """Request model for product analysis."""
    product_name: str = Field(..., min_length=2, max_length=200, description="Name of the product to analyze")


class EcoScoreResponse(BaseModel):
    """Response model for eco-scoring details."""
    overall_score: float = Field(..., description="Overall eco-friendliness score (0-100)")
    carbon_footprint: float = Field(..., description="Carbon footprint score")
    recyclability: float = Field(..., description="Recyclability score")
    sustainability: float = Field(..., description="Sustainability score")
    environmental_impact: float = Field(..., description="Environmental impact score")
    reasoning: str = Field(..., description="Detailed reasoning for the scores")


class AlternativeResponse(BaseModel):
    """Response model for alternative products."""
    name: str = Field(..., description="Alternative product name")
    eco_score: float = Field(..., description="Alternative's eco-score")
    features: List[str] = Field(..., description="Key eco-friendly features")
    brand: str = Field(..., description="Brand or manufacturer")
    availability: str = Field(default="", description="Where to find the product")


class ProductAnalysisResponse(BaseModel):
    """Response model for product analysis."""
    success: bool = Field(..., description="Whether the analysis was successful")
    product_name: str = Field(..., description="Name of the analyzed product")
    category: Optional[str] = Field(None, description="Product category")
    eco_score: Optional[EcoScoreResponse] = Field(None, description="Detailed eco-scoring")
    alternatives: List[AlternativeResponse] = Field(default_factory=list, description="Eco-friendly alternatives")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    gemini_api_configured: bool = Field(..., description="Gemini API configuration status")


# Simple Eco Scorer Class
class SimpleEcoScorer:
    """Simple eco-scoring using Gemini API directly."""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_product(self, product_name: str) -> dict:
        """Analyze a product's eco-friendliness."""
        
        prompt = f"""
        You are an environmental sustainability expert. Analyze the eco-friendliness of the product "{product_name}".
        
        Rate the product on a scale of 0-100 (100 being most eco-friendly) across these dimensions:
        - Overall eco-friendliness score
        - Carbon footprint (lower emissions = higher score)
        - Recyclability (easier to recycle = higher score) 
        - Sustainability (renewable materials, ethical production = higher score)
        - Environmental impact (less pollution/waste = higher score)
        
        Also provide 3-5 more eco-friendly alternatives to this product with better scores.
        
        Return your analysis in this EXACT JSON format:
        {{
            "product_name": "{product_name}",
            "category": "appropriate category",
            "eco_score": {{
                "overall_score": 75.5,
                "carbon_footprint": 70.0,
                "recyclability": 80.0,
                "sustainability": 75.0,
                "environmental_impact": 78.0,
                "reasoning": "Detailed explanation of the scoring"
            }},
            "alternatives": [
                {{
                    "name": "Alternative product name",
                    "eco_score": 85.0,
                    "features": ["eco-friendly feature 1", "eco-friendly feature 2"],
                    "brand": "Brand name",
                    "availability": "Where to buy"
                }}
            ]
        }}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Try to extract JSON from the response
            text = response.text.strip()
            
            # Find JSON in the response (sometimes wrapped in markdown)
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_text = text[start:end].strip()
            elif "{" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_text = text[start:end]
            else:
                json_text = text
            
            # Parse JSON
            result = json.loads(json_text)
            return {
                "success": True,
                "data": result
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse AI response: {e}",
                "raw_response": response.text[:500]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Initialize the scorer
scorer = SimpleEcoScorer()

# Create FastAPI app
app = FastAPI(
    title="Eco-Friendliness Scoring API",
    description="Simple API for analyzing product eco-friendliness using Gemini AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Eco-Friendliness Scoring API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "analyze": "POST /analyze"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    gemini_configured = bool(os.getenv("GOOGLE_API_KEY"))
    
    return HealthResponse(
        status="healthy" if gemini_configured else "degraded",
        timestamp=datetime.utcnow(),
        gemini_api_configured=gemini_configured
    )


@app.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(request: ProductAnalysisRequest):
    """
    Analyze a product's eco-friendliness and find sustainable alternatives.
    
    This endpoint analyzes a single product and returns:
    - Eco-friendliness scores across multiple dimensions
    - Detailed reasoning for the scores
    - List of more sustainable alternatives
    - Product categorization
    """
    import time
    start_time = time.time()
    
    try:
        result = await scorer.analyze_product(request.product_name)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        if result["success"]:
            data = result["data"]
            
            # Convert to response model
            response = ProductAnalysisResponse(
                success=True,
                product_name=data["product_name"],
                category=data["category"],
                eco_score=EcoScoreResponse(**data["eco_score"]),
                alternatives=[AlternativeResponse(**alt) for alt in data["alternatives"]],
                processing_time_ms=processing_time
            )
            
            return response
        
        else:
            return ProductAnalysisResponse(
                success=False,
                product_name=request.product_name,
                error=result["error"],
                processing_time_ms=processing_time
            )
    
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        
        return ProductAnalysisResponse(
            success=False,
            product_name=request.product_name,
            error=f"Internal server error: {str(e)}",
            processing_time_ms=processing_time
        )


@app.get("/test", response_model=Dict[str, Any])
async def test_endpoint():
    """Test endpoint to verify API is working."""
    return {
        "message": "API is working!",
        "timestamp": datetime.utcnow(),
        "test_analyze": "POST /analyze with {'product_name': 'iPhone 15'}",
        "gemini_configured": bool(os.getenv("GOOGLE_API_KEY"))
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow()
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    return {
        "error": "Internal server error",
        "message": str(exc),
        "status_code": 500,
        "timestamp": datetime.utcnow()
    }


# Development server
if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🌱 Starting Eco-Scoring API on {host}:{port}")
    print(f"📋 API Documentation: http://localhost:{port}/docs")
    print(f"🧪 Test endpoint: http://localhost:{port}/test")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
