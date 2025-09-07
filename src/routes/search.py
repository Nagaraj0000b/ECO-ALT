from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.product import ProductResponse, ProductListResponse, Alternative
from ..models.user import TokenData
from ..middleware.auth import get_current_user_optional


router = APIRouter(prefix="/api/search", tags=["Search & Discovery"])


@router.get("/", response_model=ProductListResponse)
async def search_products(
    query: str = Query(..., description="Search query for products"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum eco score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum eco score"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    sort_by: Optional[str] = Query("relevance", description="Sort by: relevance, eco_score, name, created_at"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of results per page"),
    skip: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Search products across the database with advanced filtering"""
    
    try:
        # TODO: Implement full-text search in MongoDB
        # database = await get_database()
        # 
        # # Build search query
        # search_query = {
        #     "$text": {"$search": query}
        # }
        # 
        # # Add filters
        # filters = []
        # if category:
        #     filters.append({"category": {"$regex": category, "$options": "i"}})
        # if min_score is not None:
        #     filters.append({"eco_score.overall_score": {"$gte": min_score}})
        # if max_score is not None:
        #     filters.append({"eco_score.overall_score": {"$lte": max_score}})
        # if brand:
        #     filters.append({"brand": {"$regex": brand, "$options": "i"}})
        # if tags:
        #     tag_list = [tag.strip() for tag in tags.split(",")]
        #     filters.append({"tags": {"$in": tag_list}})
        # 
        # if filters:
        #     search_query["$and"] = filters
        # 
        # # Build sort
        # if sort_by == "relevance":
        #     sort_spec = [("score", {"$meta": "textScore"})]
        # elif sort_by == "eco_score":
        #     sort_direction = 1 if sort_order == "asc" else -1
        #     sort_spec = [("eco_score.overall_score", sort_direction)]
        # elif sort_by == "name":
        #     sort_direction = 1 if sort_order == "asc" else -1
        #     sort_spec = [("name", sort_direction)]
        # elif sort_by == "created_at":
        #     sort_direction = 1 if sort_order == "asc" else -1
        #     sort_spec = [("created_at", sort_direction)]
        # else:
        #     sort_spec = [("score", {"$meta": "textScore"})]
        # 
        # # Execute search
        # total = await database.products.count_documents(search_query)
        # cursor = database.products.find(search_query, {"score": {"$meta": "textScore"}})
        # if sort_by == "relevance":
        #     cursor = cursor.sort(sort_spec)
        # else:
        #     cursor = cursor.sort(sort_spec)
        # cursor = cursor.skip(skip).limit(limit)
        # 
        # products = await cursor.to_list(length=limit)
        
        # For demo purposes, create mock search results
        mock_results = create_mock_search_results(query, category, min_score, max_score, brand)
        
        # Apply pagination
        total = len(mock_results)
        paginated_results = mock_results[skip:skip + limit]
        
        return ProductListResponse(
            products=paginated_results,
            total=total,
            page=skip // limit + 1,
            page_size=len(paginated_results),
            has_more=skip + len(paginated_results) < total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching products: {str(e)}"
        )


@router.get("/alternatives", response_model=List[ProductResponse])
async def get_alternatives(
    min_score: float = Query(70, ge=0, le=100, description="Minimum eco score for alternatives"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: Optional[int] = Query(10, ge=1, le=50, description="Number of alternatives to return"),
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Get eco-friendly product alternatives above a certain score threshold"""
    
    try:
        # TODO: Query database for high-scoring products
        # database = await get_database()
        # 
        # query_filter = {
        #     "eco_score.overall_score": {"$gte": min_score}
        # }
        # 
        # if category:
        #     query_filter["category"] = {"$regex": category, "$options": "i"}
        # 
        # cursor = database.products.find(query_filter).sort([
        #     ("eco_score.overall_score", -1),
        #     ("view_count", -1)
        # ]).limit(limit)
        # 
        # products = await cursor.to_list(length=limit)
        
        # For demo purposes, create mock alternatives
        alternatives = create_mock_alternatives(min_score, category, limit)
        
        return alternatives
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving alternatives: {str(e)}"
        )


@router.get("/categories", response_model=Dict[str, Any])
async def get_categories(
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Get list of available product categories with counts"""
    
    try:
        # TODO: Aggregate categories from database
        # database = await get_database()
        # 
        # pipeline = [
        #     {"$group": {
        #         "_id": "$category",
        #         "count": {"$sum": 1},
        #         "avg_score": {"$avg": "$eco_score.overall_score"}
        #     }},
        #     {"$sort": {"count": -1}},
        #     {"$limit": 50}
        # ]
        # 
        # categories = await database.products.aggregate(pipeline).to_list(length=50)
        
        # For demo purposes, return mock categories
        categories = [
            {"name": "Electronics & Technology", "count": 1250, "avg_score": 64.2},
            {"name": "Transportation", "count": 890, "avg_score": 71.5},
            {"name": "Clothing & Textiles", "count": 670, "avg_score": 58.3},
            {"name": "Food & Beverages", "count": 540, "avg_score": 67.8},
            {"name": "Personal Care & Beauty", "count": 420, "avg_score": 61.4},
            {"name": "Home & Garden", "count": 380, "avg_score": 69.1},
            {"name": "Sports & Recreation", "count": 290, "avg_score": 63.7}
        ]
        
        total_products = sum(cat["count"] for cat in categories)
        overall_avg_score = sum(cat["avg_score"] * cat["count"] for cat in categories) / total_products
        
        return {
            "categories": categories,
            "total_categories": len(categories),
            "total_products": total_products,
            "overall_avg_score": round(overall_avg_score, 1)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving categories: {str(e)}"
        )


@router.get("/trending", response_model=List[ProductResponse])
async def get_trending_products(
    period: str = Query("7d", regex="^(24h|7d|30d)$", description="Time period for trending"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: Optional[int] = Query(20, ge=1, le=50, description="Number of trending products"),
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Get trending products based on recent analysis activity"""
    
    try:
        # TODO: Calculate trending based on recent activity
        # database = await get_database()
        # 
        # # Define time range
        # if period == "24h":
        #     since = datetime.utcnow() - timedelta(hours=24)
        # elif period == "7d":
        #     since = datetime.utcnow() - timedelta(days=7)
        # else:  # 30d
        #     since = datetime.utcnow() - timedelta(days=30)
        # 
        # # Build aggregation pipeline
        # pipeline = [
        #     {"$match": {
        #         "updated_at": {"$gte": since}
        #     }},
        #     {"$addFields": {
        #         "trending_score": {
        #             "$add": [
        #                 {"$multiply": ["$view_count", 0.6]},
        #                 {"$multiply": ["$analysis_count", 0.4]}
        #             ]
        #         }
        #     }},
        #     {"$sort": {"trending_score": -1}},
        #     {"$limit": limit}
        # ]
        # 
        # if category:
        #     pipeline[0]["$match"]["category"] = {"$regex": category, "$options": "i"}
        # 
        # products = await database.products.aggregate(pipeline).to_list(length=limit)
        
        # For demo purposes, create mock trending products
        trending = create_mock_trending_products(period, category, limit)
        
        return trending
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving trending products: {str(e)}"
        )


@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Partial search query"),
    limit: Optional[int] = Query(10, ge=1, le=20, description="Number of suggestions"),
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Get search suggestions based on partial query"""
    
    try:
        # TODO: Implement search suggestions from database
        # database = await get_database()
        # 
        # # Search in product names and popular search terms
        # pipeline = [
        #     {"$match": {
        #         "name": {"$regex": f"^{re.escape(query)}", "$options": "i"}
        #     }},
        #     {"$group": {"_id": "$name", "count": {"$sum": "$view_count"}}},
        #     {"$sort": {"count": -1}},
        #     {"$limit": limit},
        #     {"$project": {"_id": 1}}
        # ]
        # 
        # results = await database.products.aggregate(pipeline).to_list(length=limit)
        # suggestions = [result["_id"] for result in results]
        
        # For demo purposes, create mock suggestions
        suggestions = create_mock_suggestions(query, limit)
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {str(e)}"
        )


def create_mock_search_results(
    query: str, 
    category: Optional[str] = None, 
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    brand: Optional[str] = None
) -> List[ProductResponse]:
    """Create mock search results for demo"""
    
    from .items import create_mock_product
    
    # Create varied results based on query
    results = []
    
    query_lower = query.lower()
    if "phone" in query_lower or "iphone" in query_lower:
        results.extend([
            create_mock_product("iPhone 15", "Electronics & Technology", 65.5, "Apple"),
            create_mock_product("iPhone 14", "Electronics & Technology", 63.2, "Apple"),
            create_mock_product("Samsung Galaxy S24", "Electronics & Technology", 68.1, "Samsung"),
            create_mock_product("Fairphone 5", "Electronics & Technology", 85.0, "Fairphone")
        ])
    
    if "car" in query_lower or "tesla" in query_lower:
        results.extend([
            create_mock_product("Tesla Model 3", "Transportation", 78.2, "Tesla"),
            create_mock_product("Tesla Model Y", "Transportation", 76.8, "Tesla"),
            create_mock_product("Toyota Prius", "Transportation", 82.1, "Toyota")
        ])
    
    if "laptop" in query_lower:
        results.extend([
            create_mock_product("MacBook Air M3", "Electronics & Technology", 69.4, "Apple"),
            create_mock_product("Framework Laptop", "Electronics & Technology", 88.5, "Framework"),
            create_mock_product("Dell XPS 13", "Electronics & Technology", 62.7, "Dell")
        ])
    
    # If no specific matches, add some general results
    if not results:
        results.extend([
            create_mock_product(f"Eco {query}", "General", 75.0, "EcoTech"),
            create_mock_product(f"Sustainable {query}", "General", 80.0, "GreenCorp")
        ])
    
    # Apply filters
    if category:
        results = [r for r in results if category.lower() in r.category.lower()]
    if min_score is not None:
        results = [r for r in results if r.eco_score.overall_score >= min_score]
    if max_score is not None:
        results = [r for r in results if r.eco_score.overall_score <= max_score]
    if brand:
        results = [r for r in results if r.brand and brand.lower() in r.brand.lower()]
    
    return results


def create_mock_alternatives(min_score: float, category: Optional[str], limit: int) -> List[ProductResponse]:
    """Create mock eco-friendly alternatives"""
    
    from .items import create_mock_product
    
    alternatives = [
        create_mock_product("Fairphone 5", "Electronics & Technology", 85.0, "Fairphone"),
        create_mock_product("Framework Laptop", "Electronics & Technology", 88.5, "Framework"),
        create_mock_product("Tesla Model 3", "Transportation", 78.2, "Tesla"),
        create_mock_product("Patagonia Jacket", "Clothing & Textiles", 82.4, "Patagonia"),
        create_mock_product("Bamboo Toothbrush", "Personal Care & Beauty", 92.1, "EcoDent"),
        create_mock_product("Solar Panel Kit", "Home & Garden", 89.7, "SolarTech"),
        create_mock_product("Organic Cotton T-Shirt", "Clothing & Textiles", 78.9, "EcoWear"),
        create_mock_product("Electric Scooter", "Transportation", 81.3, "GreenMove"),
        create_mock_product("Recycled Paper Notebook", "Office Supplies", 87.6, "EcoOffice"),
        create_mock_product("LED Light Bulb", "Home & Garden", 84.2, "BrightGreen")
    ]
    
    # Filter by score and category
    filtered = [alt for alt in alternatives if alt.eco_score.overall_score >= min_score]
    if category:
        filtered = [alt for alt in filtered if category.lower() in alt.category.lower()]
    
    return filtered[:limit]


def create_mock_trending_products(period: str, category: Optional[str], limit: int) -> List[ProductResponse]:
    """Create mock trending products"""
    
    from .items import create_mock_product
    
    trending = [
        create_mock_product("iPhone 15", "Electronics & Technology", 65.5, "Apple"),
        create_mock_product("Tesla Model 3", "Transportation", 78.2, "Tesla"),
        create_mock_product("MacBook Air M3", "Electronics & Technology", 69.4, "Apple"),
        create_mock_product("Samsung Galaxy S24", "Electronics & Technology", 68.1, "Samsung"),
        create_mock_product("Framework Laptop", "Electronics & Technology", 88.5, "Framework"),
        create_mock_product("Toyota Prius", "Transportation", 82.1, "Toyota"),
        create_mock_product("Fairphone 5", "Electronics & Technology", 85.0, "Fairphone")
    ]
    
    if category:
        trending = [p for p in trending if category.lower() in p.category.lower()]
    
    return trending[:limit]


def create_mock_suggestions(query: str, limit: int) -> List[str]:
    """Create mock search suggestions"""
    
    all_suggestions = [
        "iPhone 15", "iPhone 14", "Samsung Galaxy S24", "Tesla Model 3", 
        "MacBook Air", "iPad Pro", "Tesla Model Y", "Toyota Prius",
        "Fairphone 5", "Framework Laptop", "Dell XPS 13", "Surface Pro",
        "Google Pixel 8", "OnePlus 12", "Xiaomi Mi 13", "Sony Xperia 1",
        "Electric Scooter", "Solar Panel", "LED Light Bulb", "Bamboo Toothbrush",
        "Organic Cotton T-Shirt", "Patagonia Jacket", "Nike Air Max", "Adidas Ultraboost"
    ]
    
    # Filter suggestions that start with or contain the query
    query_lower = query.lower()
    matching = [s for s in all_suggestions if query_lower in s.lower()]
    
    return matching[:limit]
