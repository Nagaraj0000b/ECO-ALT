from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import time
from bson import ObjectId

from ..models.product import (
    ProductCreate, ProductBatch, ProductResponse, ProductListResponse,
    SearchFilters, Product, EcoScore, Alternative
)
from ..models.user import TokenData
from ..middleware.auth import get_current_user_optional
from ..services.gemini_service import GeminiService


router = APIRouter(prefix="/api/items", tags=["Items/Products"])


# Initialize Gemini service (will be properly configured in main app)
gemini_service = GeminiService()


@router.post("/", response_model=ProductResponse)
async def create_item(
    product_data: ProductCreate,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Create/analyze a new product item"""
    
    start_time = time.time()
    
    # TODO: Check database cache first
    # database = await get_database()
    # existing_product = await database.products.find_one({
    #     "name": {"$regex": f"^{re.escape(product_data.product_name)}$", "$options": "i"}
    # })
    # if existing_product:
    #     # Update view count and return cached result
    #     await database.products.update_one(
    #         {"_id": existing_product["_id"]},
    #         {"$inc": {"view_count": 1, "analysis_count": 1}}
    #     )
    #     product = Product(**existing_product)
    #     return create_product_response(product, from_cache=True, processing_time=0)
    
    try:
        # Analyze product using Gemini AI
        analysis_result = await gemini_service.analyze_product(product_data.product_name)
        
        # Create product object
        product = Product(
            name=product_data.product_name,
            category=analysis_result.get("category", "Unknown"),
            eco_score=EcoScore(**analysis_result["eco_score"]),
            alternatives=[Alternative(**alt) for alt in analysis_result.get("alternatives", [])],
            features=analysis_result.get("features", []),
            tags=analysis_result.get("tags", []),
            brand=analysis_result.get("brand"),
            created_by=ObjectId(current_user.user_id) if current_user else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # TODO: Save to database
        # result = await database.products.insert_one(product.dict(by_alias=True, exclude={"id"}))
        # product.id = result.inserted_id
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return create_product_response(product, from_cache=False, processing_time=processing_time)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing product: {str(e)}"
        )


@router.post("/batch", response_model=List[ProductResponse])
async def create_items_batch(
    batch_data: ProductBatch,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Analyze multiple products concurrently"""
    
    if len(batch_data.product_names) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 products allowed per batch request"
        )
    
    start_time = time.time()
    
    # Process products concurrently
    tasks = []
    for product_name in batch_data.product_names:
        product_create = ProductCreate(product_name=product_name)
        task = create_item(product_create, current_user)
        tasks.append(task)
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful analyses
        successful_results = []
        for result in results:
            if not isinstance(result, Exception):
                successful_results.append(result)
        
        return successful_results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch: {str(e)}"
        )


@router.get("/", response_model=ProductListResponse)
async def list_items(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum eco score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum eco score"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    sort_by: Optional[str] = Query("eco_score.overall_score", description="Sort field"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of items per page"),
    skip: Optional[int] = Query(0, ge=0, description="Number of items to skip"),
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """List products with filtering and pagination"""
    
    # TODO: Implement database query
    # database = await get_database()
    # 
    # # Build query filters
    # query_filter = {}
    # if query:
    #     query_filter["$or"] = [
    #         {"name": {"$regex": query, "$options": "i"}},
    #         {"description": {"$regex": query, "$options": "i"}},
    #         {"tags": {"$regex": query, "$options": "i"}}
    #     ]
    # if category:
    #     query_filter["category"] = {"$regex": category, "$options": "i"}
    # if min_score is not None:
    #     query_filter["eco_score.overall_score"] = {"$gte": min_score}
    # if max_score is not None:
    #     if "eco_score.overall_score" in query_filter:
    #         query_filter["eco_score.overall_score"]["$lte"] = max_score
    #     else:
    #         query_filter["eco_score.overall_score"] = {"$lte": max_score}
    # if brand:
    #     query_filter["brand"] = {"$regex": brand, "$options": "i"}
    # 
    # # Build sort
    # sort_direction = 1 if sort_order == "asc" else -1
    # sort_spec = [(sort_by, sort_direction)]
    # 
    # # Execute query
    # total = await database.products.count_documents(query_filter)
    # cursor = database.products.find(query_filter).sort(sort_spec).skip(skip).limit(limit)
    # products = await cursor.to_list(length=limit)
    # 
    # product_responses = [
    #     create_product_response(Product(**product), from_cache=True, processing_time=0)
    #     for product in products
    # ]
    
    # For demo purposes, return mock data
    mock_products = [
        create_mock_product("iPhone 15", "Electronics & Technology", 65.5, "Apple"),
        create_mock_product("Tesla Model 3", "Transportation", 78.2, "Tesla"),
        create_mock_product("Fairphone 5", "Electronics & Technology", 85.0, "Fairphone")
    ]
    
    # Apply basic filtering for demo
    filtered_products = mock_products
    if query:
        filtered_products = [p for p in filtered_products if query.lower() in p.product_name.lower()]
    if category:
        filtered_products = [p for p in filtered_products if category.lower() in p.category.lower()]
    if min_score is not None:
        filtered_products = [p for p in filtered_products if p.eco_score.overall_score >= min_score]
    if max_score is not None:
        filtered_products = [p for p in filtered_products if p.eco_score.overall_score <= max_score]
    
    total = len(filtered_products)
    paginated_products = filtered_products[skip:skip + limit]
    
    return ProductListResponse(
        products=paginated_products,
        total=total,
        page=skip // limit + 1,
        page_size=len(paginated_products),
        has_more=skip + len(paginated_products) < total
    )


@router.get("/{item_id}", response_model=ProductResponse)
async def get_item(
    item_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Get a specific product item by ID"""
    
    try:
        # TODO: Get from database
        # database = await get_database()
        # product_doc = await database.products.find_one({"_id": ObjectId(item_id)})
        # if not product_doc:
        #     raise HTTPException(status_code=404, detail="Product not found")
        # 
        # # Update view count
        # await database.products.update_one(
        #     {"_id": ObjectId(item_id)},
        #     {"$inc": {"view_count": 1}}
        # )
        # 
        # product = Product(**product_doc)
        # return create_product_response(product, from_cache=True, processing_time=0)
        
        # For demo purposes, return mock product
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid item ID format")
            
        return create_mock_product("iPhone 15", "Electronics & Technology", 65.5, "Apple")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product: {str(e)}"
        )


@router.put("/{item_id}", response_model=ProductResponse)
async def update_item(
    item_id: str,
    update_data: dict,
    current_user: TokenData = Depends(get_current_user_optional)
):
    """Update a product item (admin or creator only)"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # TODO: Check permissions and update in database
        # database = await get_database()
        # product_doc = await database.products.find_one({"_id": ObjectId(item_id)})
        # if not product_doc:
        #     raise HTTPException(status_code=404, detail="Product not found")
        # 
        # # Check if user can edit (admin or creator)
        # if not current_user.is_admin and str(product_doc.get("created_by")) != current_user.user_id:
        #     raise HTTPException(status_code=403, detail="Permission denied")
        # 
        # # Update allowed fields
        # allowed_updates = {
        #     "description": update_data.get("description"),
        #     "tags": update_data.get("tags"),
        #     "is_verified": update_data.get("is_verified") if current_user.is_admin else None
        # }
        # updates = {k: v for k, v in allowed_updates.items() if v is not None}
        # updates["updated_at"] = datetime.utcnow()
        # 
        # await database.products.update_one(
        #     {"_id": ObjectId(item_id)},
        #     {"$set": updates}
        # )
        # 
        # updated_product = await database.products.find_one({"_id": ObjectId(item_id)})
        # product = Product(**updated_product)
        # return create_product_response(product, from_cache=False, processing_time=0)
        
        # For demo purposes
        return create_mock_product("Updated iPhone 15", "Electronics & Technology", 65.5, "Apple")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product: {str(e)}"
        )


@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    current_user: TokenData = Depends(get_current_user_optional)
):
    """Delete a product item (admin or creator only)"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # TODO: Check permissions and delete from database
        # database = await get_database()
        # product_doc = await database.products.find_one({"_id": ObjectId(item_id)})
        # if not product_doc:
        #     raise HTTPException(status_code=404, detail="Product not found")
        # 
        # # Check if user can delete (admin or creator)
        # if not current_user.is_admin and str(product_doc.get("created_by")) != current_user.user_id:
        #     raise HTTPException(status_code=403, detail="Permission denied")
        # 
        # await database.products.delete_one({"_id": ObjectId(item_id)})
        
        return {"success": True, "message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {str(e)}"
        )


def create_product_response(
    product: Product, 
    from_cache: bool = False, 
    processing_time: Optional[int] = None
) -> ProductResponse:
    """Helper function to create ProductResponse from Product model"""
    
    return ProductResponse(
        success=True,
        product_name=product.name,
        category=product.category,
        eco_score=product.eco_score,
        alternatives=product.alternatives,
        brand=product.brand,
        features=product.features,
        tags=product.tags,
        from_cache=from_cache,
        processing_time_ms=processing_time,
        created_at=product.created_at,
        view_count=product.view_count,
        analysis_count=product.analysis_count
    )


def create_mock_product(name: str, category: str, score: float, brand: str) -> ProductResponse:
    """Helper function to create mock product for demo"""
    
    return ProductResponse(
        success=True,
        product_name=name,
        category=category,
        eco_score=EcoScore(
            overall_score=score,
            carbon_footprint=max(score - 5, 0),
            recyclability=min(score + 5, 100),
            sustainability=score,
            environmental_impact=min(score + 2, 100),
            reasoning=f"Mock analysis for {name}",
            confidence_score=0.85
        ),
        alternatives=[
            Alternative(
                name="Eco-Friendly Alternative",
                eco_score=min(score + 15, 100.0),
                features=["Sustainable materials", "Carbon neutral"],
                brand="EcoTech",
                comparison="More environmentally friendly option"
            )
        ],
        brand=brand,
        features=["Quality build", "Good performance"],
        tags=[category.lower().replace(" & ", "_").replace(" ", "_")],
        from_cache=False,
        processing_time_ms=2500,
        created_at=datetime.utcnow(),
        view_count=1,
        analysis_count=1
    )
