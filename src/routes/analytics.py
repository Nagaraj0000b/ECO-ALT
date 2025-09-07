from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import csv
import io

from ..models.file import DashboardStats, TrendingData, UsageReport, AnalyticsEvent
from ..models.user import TokenData
from ..middleware.auth import get_current_user, get_admin_user


router = APIRouter(prefix="/api/analytics", tags=["Analytics & Reporting"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_statistics(
    current_user: TokenData = Depends(get_admin_user)
):
    """Get dashboard statistics for admin users"""
    
    try:
        # TODO: Get real statistics from database
        # database = await get_database()
        # 
        # now = datetime.utcnow()
        # today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # 
        # # User statistics
        # total_users = await database.users.count_documents({})
        # active_users_today = await database.analytics.count_documents({
        #     "event_type": "api_call",
        #     "timestamp": {"$gte": today_start},
        #     "user_id": {"$ne": None}
        # })
        # 
        # # Product statistics
        # total_products = await database.products.count_documents({})
        # analyses_today = await database.analytics.count_documents({
        #     "event_type": "product_analysis",
        #     "timestamp": {"$gte": today_start}
        # })
        # 
        # # API statistics
        # total_api_calls = await database.analytics.count_documents({
        #     "event_type": "api_call"
        # })
        # api_calls_today = await database.analytics.count_documents({
        #     "event_type": "api_call",
        #     "timestamp": {"$gte": today_start}
        # })
        # 
        # # Average eco score
        # avg_pipeline = [
        #     {"$group": {"_id": None, "avg_score": {"$avg": "$eco_score.overall_score"}}}
        # ]
        # avg_result = await database.products.aggregate(avg_pipeline).to_list(1)
        # avg_eco_score = avg_result[0]["avg_score"] if avg_result else 0
        # 
        # # Popular categories
        # category_pipeline = [
        #     {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        #     {"$sort": {"count": -1}},
        #     {"$limit": 5}
        # ]
        # categories = await database.products.aggregate(category_pipeline).to_list(5)
        # 
        # # Recent analyses
        # recent_analyses = await database.products.find({}).sort([
        #     ("created_at", -1)
        # ]).limit(5).to_list(5)
        
        # For demo purposes, return mock statistics
        stats = DashboardStats(
            total_users=1247,
            active_users_today=89,
            total_products_analyzed=3456,
            analyses_today=234,
            total_api_calls=15678,
            api_calls_today=432,
            avg_eco_score=68.4,
            popular_categories=[
                {"name": "Electronics & Technology", "count": 1250},
                {"name": "Transportation", "count": 890},
                {"name": "Clothing & Textiles", "count": 670},
                {"name": "Food & Beverages", "count": 540},
                {"name": "Personal Care & Beauty", "count": 420}
            ],
            recent_analyses=[
                {
                    "product_name": "iPhone 15",
                    "eco_score": 65.5,
                    "created_at": datetime.utcnow() - timedelta(minutes=15),
                    "category": "Electronics & Technology"
                },
                {
                    "product_name": "Tesla Model 3",
                    "eco_score": 78.2,
                    "created_at": datetime.utcnow() - timedelta(hours=2),
                    "category": "Transportation"
                },
                {
                    "product_name": "Organic Cotton T-Shirt",
                    "eco_score": 82.1,
                    "created_at": datetime.utcnow() - timedelta(hours=4),
                    "category": "Clothing & Textiles"
                }
            ]
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard statistics: {str(e)}"
        )


@router.get("/trends", response_model=TrendingData)
async def get_trending_data(
    period: str = Query("7d", regex="^(24h|7d|30d)$", description="Time period for trends"),
    current_user: TokenData = Depends(get_admin_user)
):
    """Get trending data and usage patterns"""
    
    try:
        # TODO: Generate real trending data from analytics
        # database = await get_database()
        # 
        # if period == "24h":
        #     since = datetime.utcnow() - timedelta(hours=24)
        #     time_format = "%H:00"
        # elif period == "7d":
        #     since = datetime.utcnow() - timedelta(days=7)
        #     time_format = "%Y-%m-%d"
        # else:  # 30d
        #     since = datetime.utcnow() - timedelta(days=30)
        #     time_format = "%Y-%m-%d"
        # 
        # # API calls trend
        # api_pipeline = [
        #     {"$match": {
        #         "event_type": "api_call",
        #         "timestamp": {"$gte": since}
        #     }},
        #     {"$group": {
        #         "_id": {"$dateToString": {"format": time_format, "date": "$timestamp"}},
        #         "count": {"$sum": 1}
        #     }},
        #     {"$sort": {"_id": 1}}
        # ]
        # api_calls = await database.analytics.aggregate(api_pipeline).to_list(100)
        
        # For demo purposes, generate mock trending data
        trending_data = TrendingData(
            period=period,
            api_calls=generate_mock_time_series("api_calls", period),
            product_analyses=generate_mock_time_series("analyses", period),
            user_registrations=generate_mock_time_series("registrations", period),
            popular_products=[
                {"name": "iPhone 15", "analysis_count": 145, "avg_score": 65.5},
                {"name": "Tesla Model 3", "analysis_count": 98, "avg_score": 78.2},
                {"name": "MacBook Air M3", "analysis_count": 87, "avg_score": 69.4},
                {"name": "Samsung Galaxy S24", "analysis_count": 76, "avg_score": 68.1},
                {"name": "Framework Laptop", "analysis_count": 54, "avg_score": 88.5}
            ],
            category_distribution={
                "Electronics & Technology": 1250,
                "Transportation": 890,
                "Clothing & Textiles": 670,
                "Food & Beverages": 540,
                "Personal Care & Beauty": 420,
                "Home & Garden": 380,
                "Sports & Recreation": 290
            }
        )
        
        return trending_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving trending data: {str(e)}"
        )


@router.get("/reports/usage", response_model=UsageReport)
async def get_usage_report(
    period: str = Query("30d", regex="^(7d|30d|90d)$", description="Report period"),
    user_id: Optional[str] = Query(None, description="Specific user ID for report"),
    current_user: TokenData = Depends(get_current_user)
):
    """Generate usage report for a user or current user"""
    
    # If no user_id provided, use current user
    # If user_id provided, ensure it's admin or same user
    target_user_id = user_id or current_user.user_id
    
    if user_id and user_id != current_user.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's usage report"
        )
    
    try:
        # TODO: Generate real usage report from analytics
        # database = await get_database()
        # 
        # period_days = int(period.rstrip('d'))
        # since = datetime.utcnow() - timedelta(days=period_days)
        # 
        # # API calls count
        # api_calls = await database.analytics.count_documents({
        #     "user_id": ObjectId(target_user_id),
        #     "event_type": "api_call",
        #     "timestamp": {"$gte": since}
        # })
        # 
        # # Products analyzed
        # products_analyzed = await database.analytics.count_documents({
        #     "user_id": ObjectId(target_user_id),
        #     "event_type": "product_analysis",
        #     "timestamp": {"$gte": since}
        # })
        
        # For demo purposes, generate mock report
        usage_report = UsageReport(
            user_id=target_user_id,
            period=period,
            api_calls=127,
            products_analyzed=45,
            data_usage_mb=23.7,
            top_categories=["Electronics & Technology", "Transportation", "Clothing & Textiles"],
            favorite_products=["iPhone 15", "Tesla Model 3", "MacBook Air M3"],
            generated_at=datetime.utcnow()
        )
        
        return usage_report
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating usage report: {str(e)}"
        )


@router.post("/events")
async def log_analytics_event(
    event_data: dict,
    current_user: Optional[TokenData] = Depends(get_current_user)
):
    """Log an analytics event"""
    
    try:
        # TODO: Store analytics event in database
        # database = await get_database()
        # 
        # event = AnalyticsEvent(
        #     event_type=event_data.get("event_type", "custom"),
        #     user_id=ObjectId(current_user.user_id) if current_user else None,
        #     session_id=event_data.get("session_id"),
        #     ip_address=event_data.get("ip_address"),
        #     user_agent=event_data.get("user_agent"),
        #     endpoint=event_data.get("endpoint"),
        #     method=event_data.get("method"),
        #     status_code=event_data.get("status_code"),
        #     processing_time_ms=event_data.get("processing_time_ms"),
        #     product_name=event_data.get("product_name"),
        #     category=event_data.get("category"),
        #     eco_score=event_data.get("eco_score"),
        #     error_message=event_data.get("error_message"),
        #     metadata=event_data.get("metadata", {}),
        #     timestamp=datetime.utcnow()
        # )
        # 
        # await database.analytics.insert_one(event.dict(by_alias=True, exclude={"id"}))
        
        return {"success": True, "message": "Event logged successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging analytics event: {str(e)}"
        )


def generate_mock_time_series(metric_type: str, period: str) -> List[Dict[str, int]]:
    """Generate mock time series data for trending charts"""
    
    if period == "24h":
        # Generate hourly data for last 24 hours
        data = []
        for i in range(24):
            timestamp = datetime.utcnow() - timedelta(hours=23-i)
            hour = timestamp.strftime("%H:00")
            
            # Simulate different patterns based on metric type
            if metric_type == "api_calls":
                base_value = 20
                variation = 15 if 9 <= timestamp.hour <= 17 else 5  # Higher during work hours
            elif metric_type == "analyses":
                base_value = 12
                variation = 8 if 10 <= timestamp.hour <= 16 else 3
            else:  # registrations
                base_value = 3
                variation = 2
                
            count = base_value + (hash(f"{hour}{metric_type}") % variation)
            data.append({"date": hour, "count": count})
        
    elif period == "7d":
        # Generate daily data for last 7 days
        data = []
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=6-i)
            date_str = date.strftime("%Y-%m-%d")
            
            if metric_type == "api_calls":
                base_value = 400
                variation = 200
            elif metric_type == "analyses":
                base_value = 150
                variation = 80
            else:  # registrations
                base_value = 25
                variation = 15
                
            # Weekend effect
            is_weekend = date.weekday() >= 5
            if is_weekend:
                base_value = int(base_value * 0.7)
                
            count = base_value + (hash(f"{date_str}{metric_type}") % variation)
            data.append({"date": date_str, "count": count})
            
    else:  # 30d
        # Generate daily data for last 30 days
        data = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=29-i)
            date_str = date.strftime("%Y-%m-%d")
            
            if metric_type == "api_calls":
                base_value = 350
                variation = 150
            elif metric_type == "analyses":
                base_value = 120
                variation = 60
            else:  # registrations
                base_value = 20
                variation = 12
                
            # Weekend and trend effects
            is_weekend = date.weekday() >= 5
            if is_weekend:
                base_value = int(base_value * 0.8)
                
            # Add slight upward trend
            trend_factor = 1 + (i / 30 * 0.1)  # 10% growth over period
            base_value = int(base_value * trend_factor)
                
            count = base_value + (hash(f"{date_str}{metric_type}") % variation)
            data.append({"date": date_str, "count": count})
    
    return data
