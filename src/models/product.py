from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId


class EcoScore(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    carbon_footprint: float = Field(..., ge=0, le=100)
    recyclability: float = Field(..., ge=0, le=100)
    sustainability: float = Field(..., ge=0, le=100)
    environmental_impact: float = Field(..., ge=0, le=100)
    reasoning: str
    confidence_score: float = Field(..., ge=0, le=1)


class Alternative(BaseModel):
    name: str
    eco_score: float = Field(..., ge=0, le=100)
    features: List[str] = Field(default_factory=list)
    brand: Optional[str] = None
    comparison: Optional[str] = None
    availability: Optional[str] = None
    price_range: Optional[str] = None
    website: Optional[str] = None


class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=200)
    category: str
    description: Optional[str] = None
    brand: Optional[str] = None
    eco_score: EcoScore
    alternatives: List[Alternative] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    price_range: Optional[str] = None
    availability: Optional[str] = None
    website: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    analysis_version: str = Field(default="1.0")
    view_count: int = Field(default=0)
    analysis_count: int = Field(default=1)
    is_verified: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "iPhone 15",
                "category": "Electronics & Technology",
                "brand": "Apple",
                "eco_score": {
                    "overall_score": 65.5,
                    "carbon_footprint": 60.0,
                    "recyclability": 70.0,
                    "sustainability": 65.0,
                    "environmental_impact": 68.0,
                    "reasoning": "Good recyclability but high carbon footprint",
                    "confidence_score": 0.85
                },
                "alternatives": [
                    {
                        "name": "Fairphone 5",
                        "eco_score": 85.0,
                        "features": ["Modular design", "Fair trade"],
                        "brand": "Fairphone"
                    }
                ],
                "tags": ["smartphone", "electronics", "premium"]
            }
        }


class ProductCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, alias="product_name")


class ProductBatch(BaseModel):
    product_names: List[str] = Field(..., max_items=10)


class ProductUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_verified: Optional[bool] = None


class ProductResponse(BaseModel):
    success: bool = True
    product_name: str
    category: str
    eco_score: EcoScore
    alternatives: List[Alternative]
    brand: Optional[str] = None
    features: List[str]
    tags: List[str]
    from_cache: bool = False
    processing_time_ms: Optional[int] = None
    created_at: datetime
    view_count: int
    analysis_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "product_name": "iPhone 15",
                "category": "Electronics & Technology",
                "eco_score": {
                    "overall_score": 65.5,
                    "carbon_footprint": 60.0,
                    "recyclability": 70.0,
                    "sustainability": 65.0,
                    "environmental_impact": 68.0,
                    "reasoning": "Analysis details...",
                    "confidence_score": 0.85
                },
                "alternatives": [],
                "brand": "Apple",
                "features": ["Premium build", "Long support"],
                "tags": ["smartphone", "electronics"],
                "from_cache": False,
                "processing_time_ms": 3500,
                "view_count": 42,
                "analysis_count": 1
            }
        }


class SearchFilters(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)
    brand: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = Field(default="eco_score.overall_score", pattern="^(name|eco_score.overall_score|created_at|view_count|analysis_count)$")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")
    limit: Optional[int] = Field(default=20, ge=1, le=100)
    skip: Optional[int] = Field(default=0, ge=0)


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
