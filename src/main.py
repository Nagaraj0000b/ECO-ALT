from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import os
import logging
from typing import Dict, Any

# Import route modules
from .routes import auth, items, search, analytics, admin, utils, files
from .middleware.auth import rate_limit_middleware, subscription_middleware
from .services.gemini_service import GeminiService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Application lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🌱 ECO-ALT API starting up...")
    
    # Initialize services
    gemini_service = GeminiService()
    logger.info("✅ Gemini service initialized")
    
    # TODO: Initialize database connection
    # database = await connect_to_database()
    # logger.info("✅ Database connection established")
    
    # TODO: Initialize cache
    # cache = await initialize_cache()
    # logger.info("✅ Cache initialized")
    
    logger.info("🚀 ECO-ALT API startup complete!")
    
    yield
    
    # Shutdown
    logger.info("🔄 ECO-ALT API shutting down...")
    
    # TODO: Close database connections
    # await database.close()
    
    # TODO: Close cache connections
    # await cache.close()
    
    logger.info("👋 ECO-ALT API shutdown complete!")


# Create FastAPI application
app = FastAPI(
    title="ECO-ALT API",
    description="""
    🌱 **AI-Powered Eco-Friendliness Scoring Backend**
    
    A comprehensive system for analyzing product eco-friendliness using Google Gemini AI 
    and providing sustainable alternatives.
    
    ## Features
    
    * **AI-Powered Analysis**: Google Gemini integration for intelligent product evaluation
    * **Comprehensive Scoring**: Multi-dimensional eco-scoring system
    * **Alternative Discovery**: Smart recommendations for eco-friendly products
    * **User Management**: Complete authentication and authorization system
    * **Search & Discovery**: Advanced filtering and search capabilities
    * **Analytics & Reporting**: Detailed insights and usage statistics
    * **Admin Dashboard**: System management and monitoring tools
    
    ## Authentication
    
    Most endpoints require authentication using JWT tokens. Register for an account
    or login to get your access token.
    
    ## Rate Limits
    
    - **Free Tier**: 20 requests/hour
    - **Premium Tier**: 100 requests/hour  
    - **Enterprise Tier**: 1000 requests/hour
    
    ## Support
    
    For questions or support, please contact our team or submit feedback through the API.
    """,
    version="1.0.0",
    terms_of_service="https://ecoalt.com/terms",
    contact={
        "name": "ECO-ALT Support",
        "url": "https://ecoalt.com/support",
        "email": "support@ecoalt.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"]
)

# Trusted host middleware (security)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # In production, specify exact hosts
)


# Custom middleware for request logging and timing
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log requests and add timing headers"""
    
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        process_time_ms = int(process_time * 1000)
        
        # Add headers
        response.headers["X-Process-Time"] = str(process_time_ms)
        response.headers["X-Server"] = "ECO-ALT-API"
        
        # Log response
        logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time_ms}ms")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        process_time_ms = int(process_time * 1000)
        
        logger.error(f"❌ {request.method} {request.url.path} - Error: {str(e)} - {process_time_ms}ms")
        raise


# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to responses"""
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Subscription checking middleware  
app.middleware("http")(subscription_middleware)


# Global exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": time.time()
        }
    )


@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Custom validation error handler"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors() if hasattr(exc, 'errors') else str(exc),
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error on {request.method} {request.url.path}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
            "timestamp": time.time(),
            "request_id": str(hash(f"{time.time()}{request.url.path}"))[:8]
        }
    )


# Include all route modules
app.include_router(utils.router)  # Utility routes (no prefix)
app.include_router(auth.router)   # Authentication routes
app.include_router(items.router)  # Product/item routes
app.include_router(search.router) # Search routes
app.include_router(analytics.router) # Analytics routes
app.include_router(admin.router)  # Admin routes
app.include_router(files.router)  # File management routes

# Legacy analyze endpoint (for backward compatibility)
@app.post("/analyze")
async def legacy_analyze_endpoint(request: Request):
    """Legacy analyze endpoint - redirects to /api/items/"""
    
    logger.info("Redirecting legacy /analyze request to /api/items/")
    
    # Forward to the new endpoint
    from .routes.items import create_item
    from .models.product import ProductCreate
    
    try:
        request_data = await request.json()
        product_data = ProductCreate(**request_data)
        return await create_item(product_data, None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request format: {str(e)}"
        )


# Health check endpoint (additional public endpoint)
@app.get("/ping")
async def ping():
    """Simple ping endpoint for load balancers"""
    return {"status": "ok", "timestamp": time.time()}


# Application info
@app.get("/info")
async def app_info():
    """Get application information"""
    return {
        "name": "ECO-ALT API",
        "version": "1.0.0",
        "description": "AI-powered eco-friendliness scoring backend",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "python_version": "3.11+",
        "fastapi_version": "0.104.1",
        "features": [
            "AI-powered product analysis",
            "Eco-friendliness scoring",
            "Alternative recommendations",
            "User authentication",
            "Search and filtering",
            "Analytics and reporting",
            "Admin dashboard"
        ],
        "endpoints": {
            "authentication": "/api/auth/*",
            "products": "/api/items/*", 
            "search": "/api/search/*",
            "analytics": "/api/analytics/*",
            "admin": "/api/admin/*",
            "documentation": "/docs",
            "health": "/health"
        }
    }


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🌱 Starting ECO-ALT API server on {host}:{port}")
    logger.info(f"📖 Documentation available at http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug",
        access_log=True
    )
