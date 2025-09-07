from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

from ..models.user import TokenData
from ..middleware.auth import get_current_user_optional


router = APIRouter(tags=["Utility Endpoints"])


@router.get("/")
async def root():
    """API root endpoint with basic information"""
    
    return {
        "name": "ECO-ALT API",
        "description": "AI-powered eco-friendliness scoring backend",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "timestamp": datetime.utcnow(),
        "features": [
            "Product eco-scoring analysis",
            "AI-powered alternative discovery",
            "Comprehensive search and filtering",
            "User authentication and management",
            "Analytics and reporting",
            "Admin dashboard"
        ]
    }


@router.get("/health")
async def health_check():
    """Public health check endpoint"""
    
    try:
        # TODO: Check basic system components
        # database_responsive = await ping_database()
        # api_responsive = await ping_gemini_api()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0",
            "uptime_hours": 360,  # Mock uptime
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        return health_status
        
    except Exception as e:
        # Return degraded status if any issues
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow(),
            "error": "Some services may be unavailable",
            "details": str(e)
        }


@router.get("/config")
async def get_public_configuration():
    """Get public configuration settings"""
    
    config = {
        "api_version": "1.0.0",
        "max_batch_size": 10,
        "supported_categories": [
            "Electronics & Technology",
            "Transportation",
            "Clothing & Textiles",
            "Food & Beverages",
            "Personal Care & Beauty",
            "Home & Garden",
            "Sports & Recreation",
            "Office Supplies"
        ],
        "eco_score_range": {
            "min": 0,
            "max": 100
        },
        "rate_limits": {
            "free_tier": {
                "requests_per_hour": 20,
                "batch_size": 3
            },
            "premium_tier": {
                "requests_per_hour": 100,
                "batch_size": 10
            },
            "enterprise_tier": {
                "requests_per_hour": 1000,
                "batch_size": 10
            }
        },
        "features": {
            "ai_analysis": True,
            "alternative_discovery": True,
            "batch_processing": True,
            "search_filters": True,
            "user_analytics": True,
            "export_data": True
        },
        "supported_file_types": [
            "image/jpeg",
            "image/png",
            "image/webp",
            "application/pdf"
        ],
        "max_file_size_mb": 10,
        "cache_duration_seconds": 3600,
        "maintenance_mode": False
    }
    
    return config


@router.get("/version")
async def get_version_info():
    """Get detailed version information"""
    
    version_info = {
        "api_version": "1.0.0",
        "build_date": "2024-01-15T10:30:00Z",
        "git_commit": "abc123def456",  # Mock commit hash
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": "3.11.0",
        "dependencies": {
            "fastapi": "0.104.1",
            "pydantic": "2.5.0",
            "google-generativeai": "0.8.3",
            "uvicorn": "0.24.0"
        },
        "features_changelog": {
            "1.0.0": [
                "Initial release",
                "AI-powered eco-scoring",
                "User authentication",
                "Search and discovery",
                "Admin dashboard",
                "Analytics and reporting"
            ]
        },
        "api_endpoints_count": 45,
        "supported_models": ["gemini-1.5-flash"],
        "database_version": "MongoDB 7.0",
        "deployment_timestamp": datetime.utcnow() - timedelta(days=15)
    }
    
    return version_info


@router.get("/categories")
async def get_product_categories():
    """Get list of supported product categories"""
    
    categories = [
        {
            "name": "Electronics & Technology",
            "description": "Smartphones, laptops, computers, and electronic devices",
            "examples": ["iPhone", "MacBook", "Smart TV", "Gaming Console"],
            "typical_score_range": [45, 85]
        },
        {
            "name": "Transportation",
            "description": "Vehicles, bikes, scooters, and transportation methods",
            "examples": ["Electric Car", "Bicycle", "Public Transit", "Scooter"],
            "typical_score_range": [35, 95]
        },
        {
            "name": "Clothing & Textiles",
            "description": "Apparel, footwear, and textile products",
            "examples": ["Organic Cotton T-Shirt", "Sustainable Jeans", "Eco Sneakers"],
            "typical_score_range": [25, 90]
        },
        {
            "name": "Food & Beverages",
            "description": "Food items, drinks, and consumable products",
            "examples": ["Organic Food", "Plant-based Milk", "Local Produce"],
            "typical_score_range": [40, 95]
        },
        {
            "name": "Personal Care & Beauty",
            "description": "Cosmetics, hygiene products, and personal care items",
            "examples": ["Organic Soap", "Bamboo Toothbrush", "Natural Shampoo"],
            "typical_score_range": [30, 92]
        },
        {
            "name": "Home & Garden",
            "description": "Household items, furniture, and gardening products",
            "examples": ["Solar Panel", "LED Bulb", "Compost Bin", "Bamboo Furniture"],
            "typical_score_range": [35, 95]
        },
        {
            "name": "Sports & Recreation",
            "description": "Sports equipment, outdoor gear, and recreational items",
            "examples": ["Sustainable Yoga Mat", "Recycled Frisbee", "Eco Camping Gear"],
            "typical_score_range": [40, 88]
        },
        {
            "name": "Office Supplies",
            "description": "Work-related items and office equipment",
            "examples": ["Recycled Paper", "Refillable Pen", "Solar Calculator"],
            "typical_score_range": [45, 90]
        }
    ]
    
    return {
        "categories": categories,
        "total_categories": len(categories),
        "last_updated": datetime.utcnow(),
        "scoring_methodology": "Categories are scored based on manufacturing impact, material sustainability, energy efficiency, and end-of-life disposal options."
    }


@router.get("/statistics")
async def get_public_statistics(
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Get public system statistics"""
    
    # Basic stats available to everyone
    public_stats = {
        "total_products_analyzed": 3456,
        "total_categories": 8,
        "avg_eco_score": 68.4,
        "analyses_this_month": 12456,
        "top_categories": [
            {"name": "Electronics & Technology", "count": 1250},
            {"name": "Transportation", "count": 890},
            {"name": "Clothing & Textiles", "count": 670}
        ],
        "sustainability_impact": {
            "carbon_footprint_awareness": "87% of users report increased awareness",
            "alternative_adoption": "34% users switched to recommended alternatives",
            "avg_score_improvement": "+12.3 points over 6 months"
        }
    }
    
    # Add user-specific stats if authenticated
    if current_user:
        public_stats["user_stats"] = {
            "your_analyses": 45,
            "your_avg_score": 72.1,
            "eco_improvements": "+8.4 points this month",
            "favorite_categories": ["Electronics & Technology", "Transportation"]
        }
    
    return public_stats


@router.get("/status")
async def get_system_status():
    """Get current system operational status"""
    
    status_info = {
        "operational_status": "online",
        "maintenance_mode": False,
        "last_maintenance": "2024-01-10T02:00:00Z",
        "next_scheduled_maintenance": "2024-02-15T02:00:00Z",
        "service_availability": {
            "api": "100%",
            "ai_analysis": "99.8%",
            "database": "99.9%",
            "file_storage": "100%"
        },
        "current_load": {
            "api_requests_per_minute": 45,
            "active_users": 23,
            "queue_length": 0
        },
        "incident_history": {
            "last_30_days": 0,
            "last_incident": None,
            "avg_resolution_time_minutes": 12
        }
    }
    
    return status_info


@router.post("/feedback")
async def submit_feedback(
    feedback_data: Dict[str, Any],
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Submit user feedback"""
    
    try:
        # TODO: Store feedback in database
        # feedback = {
        #     "user_id": current_user.user_id if current_user else None,
        #     "type": feedback_data.get("type", "general"),
        #     "message": feedback_data.get("message", ""),
        #     "rating": feedback_data.get("rating"),
        #     "category": feedback_data.get("category"),
        #     "timestamp": datetime.utcnow(),
        #     "status": "new"
        # }
        # await database.feedback.insert_one(feedback)
        
        return {
            "success": True,
            "message": "Thank you for your feedback! We'll review it shortly.",
            "feedback_id": "fb_" + str(hash(str(datetime.utcnow())))[:8],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/limits")
async def get_user_limits(
    current_user: TokenData = Depends(get_current_user_optional)
):
    """Get current user's API limits and usage"""
    
    if not current_user:
        # Return free tier limits for unauthenticated users
        return {
            "tier": "anonymous",
            "requests_per_hour": 5,
            "requests_per_day": 20,
            "batch_size_limit": 1,
            "current_usage": {
                "requests_this_hour": 0,
                "requests_today": 0,
                "reset_time": datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            }
        }
    
    # TODO: Get real usage from database
    # current_usage = await get_user_usage(current_user.user_id)
    
    tier_limits = {
        "free": {"requests_per_hour": 20, "requests_per_day": 100, "batch_size": 3},
        "premium": {"requests_per_hour": 100, "requests_per_day": 1000, "batch_size": 10},
        "enterprise": {"requests_per_hour": 1000, "requests_per_day": 10000, "batch_size": 10}
    }
    
    limits = tier_limits.get(current_user.subscription_tier, tier_limits["free"])
    
    return {
        "tier": current_user.subscription_tier,
        "requests_per_hour": limits["requests_per_hour"],
        "requests_per_day": limits["requests_per_day"],
        "batch_size_limit": limits["batch_size"],
        "current_usage": {
            "requests_this_hour": 12,  # Mock usage
            "requests_today": 67,
            "reset_time": datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        },
        "upgrade_available": current_user.subscription_tier == "free"
    }
