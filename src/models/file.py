from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId


class FileMetadata(BaseModel):
    filename: str
    original_filename: str
    content_type: str
    size: int
    checksum: str
    width: Optional[int] = None  # for images
    height: Optional[int] = None  # for images
    duration: Optional[float] = None  # for videos/audio


class UploadedFile(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    filename: str
    original_filename: str
    file_path: str
    content_type: str
    size: int
    checksum: str
    metadata: FileMetadata
    uploaded_by: PyObjectId
    is_public: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    download_count: int = Field(default=0)
    expires_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FileUploadResponse(BaseModel):
    success: bool = True
    file_id: str
    filename: str
    size: int
    content_type: str
    url: str
    created_at: datetime


class AnalyticsEvent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    event_type: str  # api_call, product_analysis, user_registration, file_upload, etc.
    user_id: Optional[PyObjectId] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    processing_time_ms: Optional[int] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    eco_score: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DashboardStats(BaseModel):
    total_users: int
    active_users_today: int
    total_products_analyzed: int
    analyses_today: int
    total_api_calls: int
    api_calls_today: int
    avg_eco_score: float
    popular_categories: List[Dict[str, Any]]
    recent_analyses: List[Dict[str, Any]]


class TrendingData(BaseModel):
    period: str  # "24h", "7d", "30d"
    api_calls: List[Dict[str, int]]  # [{"date": "2023-10-01", "count": 150}]
    product_analyses: List[Dict[str, int]]
    user_registrations: List[Dict[str, int]]
    popular_products: List[Dict[str, Any]]
    category_distribution: Dict[str, int]


class UsageReport(BaseModel):
    user_id: str
    period: str
    api_calls: int
    products_analyzed: int
    data_usage_mb: float
    top_categories: List[str]
    favorite_products: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
