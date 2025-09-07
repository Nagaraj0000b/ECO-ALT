from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..models.user import TokenData, UserResponse
from ..middleware.auth import get_admin_user


router = APIRouter(prefix="/api/admin", tags=["Admin/Management"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: Optional[int] = Query(50, ge=1, le=200, description="Number of users per page"),
    skip: Optional[int] = Query(0, ge=0, description="Number of users to skip"),
    search: Optional[str] = Query(None, description="Search users by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    subscription_tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    current_user: TokenData = Depends(get_admin_user)
):
    """List all users (admin only)"""
    
    try:
        # TODO: Get users from database
        # database = await get_database()
        # 
        # # Build query filters
        # query_filter = {}
        # if search:
        #     query_filter["$or"] = [
        #         {"first_name": {"$regex": search, "$options": "i"}},
        #         {"last_name": {"$regex": search, "$options": "i"}},
        #         {"email": {"$regex": search, "$options": "i"}},
        #         {"username": {"$regex": search, "$options": "i"}}
        #     ]
        # if is_active is not None:
        #     query_filter["is_active"] = is_active
        # if subscription_tier:
        #     query_filter["subscription_tier"] = subscription_tier
        # 
        # # Execute query
        # cursor = database.users.find(query_filter).sort([
        #     ("created_at", -1)
        # ]).skip(skip).limit(limit)
        # 
        # users_data = await cursor.to_list(length=limit)
        # users = [UserResponse(**user_data) for user_data in users_data]
        
        # For demo purposes, return mock users
        mock_users = [
            UserResponse(
                id="60f1234567890abcdef12345",
                username="johndoe",
                email="john@example.com",
                first_name="John",
                last_name="Doe",
                is_active=True,
                is_admin=False,
                is_verified=True,
                profile={"bio": "Eco enthusiast", "location": "San Francisco, CA"},
                created_at=datetime.utcnow() - timedelta(days=30),
                last_login=datetime.utcnow() - timedelta(hours=2),
                api_calls_count=45,
                subscription_tier="premium"
            ),
            UserResponse(
                id="60f1234567890abcdef12346",
                username="janedoe",
                email="jane@example.com",
                first_name="Jane",
                last_name="Smith",
                is_active=True,
                is_admin=False,
                is_verified=True,
                profile={"bio": "Sustainability advocate", "location": "Portland, OR"},
                created_at=datetime.utcnow() - timedelta(days=15),
                last_login=datetime.utcnow() - timedelta(hours=24),
                api_calls_count=128,
                subscription_tier="free"
            ),
            UserResponse(
                id="60f1234567890abcdef12347",
                username="admin",
                email="admin@ecoalt.com",
                first_name="Admin",
                last_name="User",
                is_active=True,
                is_admin=True,
                is_verified=True,
                profile={"bio": "System administrator", "location": "Remote"},
                created_at=datetime.utcnow() - timedelta(days=100),
                last_login=datetime.utcnow() - timedelta(minutes=30),
                api_calls_count=2156,
                subscription_tier="enterprise"
            )
        ]
        
        # Apply filters for demo
        filtered_users = mock_users
        if search:
            search_lower = search.lower()
            filtered_users = [
                u for u in filtered_users 
                if search_lower in u.first_name.lower() 
                or search_lower in u.last_name.lower()
                or search_lower in u.email.lower()
                or search_lower in u.username.lower()
            ]
        if is_active is not None:
            filtered_users = [u for u in filtered_users if u.is_active == is_active]
        if subscription_tier:
            filtered_users = [u for u in filtered_users if u.subscription_tier == subscription_tier]
        
        return filtered_users[skip:skip + limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: TokenData = Depends(get_admin_user)
):
    """Update user active status (admin only)"""
    
    try:
        # TODO: Update user status in database
        # database = await get_database()
        # 
        # result = await database.users.update_one(
        #     {"_id": ObjectId(user_id)},
        #     {"$set": {
        #         "is_active": is_active,
        #         "updated_at": datetime.utcnow()
        #     }}
        # )
        # 
        # if result.matched_count == 0:
        #     raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "message": f"User {'activated' if is_active else 'deactivated'} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user status: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_system_statistics(
    current_user: TokenData = Depends(get_admin_user)
):
    """Get comprehensive system statistics (admin only)"""
    
    try:
        # TODO: Get real system statistics
        # database = await get_database()
        # 
        # # User statistics
        # user_stats = await database.users.aggregate([
        #     {"$group": {
        #         "_id": None,
        #         "total_users": {"$sum": 1},
        #         "active_users": {"$sum": {"$cond": ["$is_active", 1, 0]}},
        #         "verified_users": {"$sum": {"$cond": ["$is_verified", 1, 0]}},
        #         "admin_users": {"$sum": {"$cond": ["$is_admin", 1, 0]}}
        #     }}
        # ]).to_list(1)
        # 
        # # Product statistics
        # product_stats = await database.products.aggregate([
        #     {"$group": {
        #         "_id": None,
        #         "total_products": {"$sum": 1},
        #         "verified_products": {"$sum": {"$cond": ["$is_verified", 1, 0]}},
        #         "avg_eco_score": {"$avg": "$eco_score.overall_score"},
        #         "total_views": {"$sum": "$view_count"},
        #         "total_analyses": {"$sum": "$analysis_count"}
        #     }}
        # ]).to_list(1)
        # 
        # # API statistics
        # now = datetime.utcnow()
        # today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # 
        # api_stats = await database.analytics.aggregate([
        #     {"$group": {
        #         "_id": None,
        #         "total_api_calls": {"$sum": 1},
        #         "api_calls_today": {
        #             "$sum": {"$cond": [{"$gte": ["$timestamp", today_start]}, 1, 0]}
        #         },
        #         "avg_response_time": {"$avg": "$processing_time_ms"},
        #         "error_rate": {
        #             "$avg": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}
        #         }
        #     }}
        # ]).to_list(1)
        
        # For demo purposes, return mock statistics
        stats = {
            "users": {
                "total_users": 1247,
                "active_users": 1198,
                "verified_users": 1089,
                "admin_users": 3,
                "new_users_today": 12,
                "subscription_distribution": {
                    "free": 892,
                    "premium": 298,
                    "enterprise": 57
                }
            },
            "products": {
                "total_products": 3456,
                "verified_products": 2134,
                "avg_eco_score": 68.4,
                "total_views": 156789,
                "total_analyses": 89456,
                "analyses_today": 234,
                "category_distribution": {
                    "Electronics & Technology": 1250,
                    "Transportation": 890,
                    "Clothing & Textiles": 670,
                    "Food & Beverages": 540,
                    "Personal Care & Beauty": 420
                }
            },
            "api": {
                "total_api_calls": 156789,
                "api_calls_today": 1245,
                "avg_response_time_ms": 2847,
                "error_rate": 0.024,
                "uptime": 99.97,
                "popular_endpoints": [
                    {"/api/analyze": 45234},
                    {"/api/search": 23456},
                    {"/api/items": 18765},
                    {"/api/auth/login": 12345},
                    {"/api/alternatives": 9876}
                ]
            },
            "system": {
                "server_start_time": datetime.utcnow() - timedelta(days=15, hours=3),
                "database_size_mb": 2456.7,
                "cache_hit_rate": 0.847,
                "active_connections": 47,
                "memory_usage_mb": 512.3,
                "cpu_usage_percent": 23.4
            }
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system statistics: {str(e)}"
        )


@router.get("/health")
async def health_check(
    current_user: TokenData = Depends(get_admin_user)
):
    """Detailed health check endpoint (admin only)"""
    
    try:
        # TODO: Check all system components
        # database_status = await check_database_health()
        # gemini_status = await check_gemini_api_health()
        # cache_status = await check_cache_health()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0",
            "components": {
                "database": {
                    "status": "healthy",
                    "response_time_ms": 45,
                    "connections": 12
                },
                "gemini_api": {
                    "status": "healthy",
                    "response_time_ms": 1234,
                    "quota_remaining": 8752
                },
                "cache": {
                    "status": "healthy",
                    "hit_rate": 0.847,
                    "memory_usage_mb": 128.5
                },
                "file_storage": {
                    "status": "healthy",
                    "available_space_gb": 245.6,
                    "total_files": 1456
                }
            },
            "metrics": {
                "uptime_seconds": 1296000,  # 15 days
                "total_requests": 156789,
                "active_users": 47,
                "error_rate": 0.024
            }
        }
        
        return health_status
        
    except Exception as e:
        # Return unhealthy status if any component fails
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e),
            "components": {
                "database": {"status": "unknown"},
                "gemini_api": {"status": "unknown"},
                "cache": {"status": "unknown"},
                "file_storage": {"status": "unknown"}
            }
        }


@router.post("/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    message: Optional[str] = None,
    current_user: TokenData = Depends(get_admin_user)
):
    """Toggle maintenance mode (admin only)"""
    
    try:
        # TODO: Set maintenance mode in cache/database
        # await set_maintenance_mode(enabled, message)
        
        return {
            "success": True,
            "maintenance_mode": enabled,
            "message": message or ("Maintenance mode enabled" if enabled else "Maintenance mode disabled"),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling maintenance mode: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache(
    cache_type: str = Query("all", description="Type of cache to clear: all, products, users, analytics"),
    current_user: TokenData = Depends(get_admin_user)
):
    """Clear system cache (admin only)"""
    
    try:
        # TODO: Clear specified cache
        # if cache_type == "all":
        #     await clear_all_cache()
        # elif cache_type == "products":
        #     await clear_product_cache()
        # elif cache_type == "users":
        #     await clear_user_cache()
        # elif cache_type == "analytics":
        #     await clear_analytics_cache()
        # else:
        #     raise ValueError(f"Unknown cache type: {cache_type}")
        
        return {
            "success": True,
            "message": f"{cache_type.title()} cache cleared successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.get("/logs")
async def get_system_logs(
    level: str = Query("INFO", description="Log level: DEBUG, INFO, WARNING, ERROR"),
    limit: int = Query(100, ge=1, le=1000, description="Number of log entries"),
    since: Optional[str] = Query(None, description="Get logs since timestamp (ISO format)"),
    current_user: TokenData = Depends(get_admin_user)
):
    """Get system logs (admin only)"""
    
    try:
        # TODO: Retrieve logs from logging system
        # since_datetime = datetime.fromisoformat(since) if since else datetime.utcnow() - timedelta(hours=24)
        # logs = await get_logs_from_database(level, limit, since_datetime)
        
        # For demo purposes, return mock logs
        mock_logs = [
            {
                "timestamp": datetime.utcnow() - timedelta(minutes=5),
                "level": "INFO",
                "message": "Product analysis completed for iPhone 15",
                "module": "gemini_service",
                "user_id": "60f1234567890abcdef12345"
            },
            {
                "timestamp": datetime.utcnow() - timedelta(minutes=12),
                "level": "WARNING",
                "message": "High API usage detected for user premium_user_001",
                "module": "rate_limiter",
                "user_id": "60f1234567890abcdef12346"
            },
            {
                "timestamp": datetime.utcnow() - timedelta(hours=1),
                "level": "INFO",
                "message": "New user registration: jane@example.com",
                "module": "auth",
                "user_id": None
            },
            {
                "timestamp": datetime.utcnow() - timedelta(hours=2),
                "level": "ERROR",
                "message": "Gemini API rate limit exceeded",
                "module": "gemini_service",
                "user_id": None
            }
        ]
        
        # Filter by level
        if level != "DEBUG":
            level_order = {"INFO": 1, "WARNING": 2, "ERROR": 3}
            min_level = level_order.get(level, 1)
            mock_logs = [
                log for log in mock_logs 
                if level_order.get(log["level"], 0) >= min_level
            ]
        
        return {
            "logs": mock_logs[:limit],
            "total_count": len(mock_logs),
            "level_filter": level,
            "retrieved_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving logs: {str(e)}"
        )
