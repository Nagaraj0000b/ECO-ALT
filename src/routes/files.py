from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
import os
import hashlib
import shutil
from pathlib import Path

from ..models.file import FileUploadResponse, UploadedFile, FileMetadata
from ..models.user import TokenData
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/api/files", tags=["File & Media Management"])

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "application/pdf", "text/plain", "text/csv"
}


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = None,
    tags: Optional[str] = None,
    is_public: bool = False,
    current_user: TokenData = Depends(get_current_user)
):
    """Upload a file"""
    
    # Validate file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Generate unique filename
        file_hash = hashlib.sha256(file_content).hexdigest()[:16]
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{file_hash}_{int(datetime.utcnow().timestamp())}{file_extension}"
        
        # Create user directory
        user_dir = UPLOAD_DIR / current_user.user_id
        user_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = user_dir / unique_filename
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Create file metadata
        file_metadata = FileMetadata(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            content_type=file.content_type,
            size=len(file_content),
            checksum=file_hash
        )
        
        # TODO: Save to database
        # uploaded_file = UploadedFile(
        #     filename=unique_filename,
        #     original_filename=file.filename or "unknown",
        #     file_path=str(file_path),
        #     content_type=file.content_type,
        #     size=len(file_content),
        #     checksum=file_hash,
        #     metadata=file_metadata,
        #     uploaded_by=ObjectId(current_user.user_id),
        #     is_public=is_public,
        #     tags=tags.split(',') if tags else [],
        #     description=description,
        #     created_at=datetime.utcnow()
        # )
        # 
        # result = await database.files.insert_one(uploaded_file.dict(by_alias=True, exclude={"id"}))
        # uploaded_file.id = result.inserted_id
        
        return FileUploadResponse(
            success=True,
            file_id=f"file_{file_hash}",
            filename=unique_filename,
            size=len(file_content),
            content_type=file.content_type,
            url=f"/api/files/{unique_filename}",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        # Clean up file if database save failed
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/{file_id}")
async def serve_file(
    file_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user)
):
    """Serve/download a file"""
    
    try:
        # TODO: Get file info from database
        # database = await get_database()
        # file_doc = await database.files.find_one({"_id": ObjectId(file_id)})
        # if not file_doc:
        #     raise HTTPException(status_code=404, detail="File not found")
        # 
        # uploaded_file = UploadedFile(**file_doc)
        # 
        # # Check access permissions
        # if not uploaded_file.is_public:
        #     if not current_user:
        #         raise HTTPException(status_code=401, detail="Authentication required")
        #     if str(uploaded_file.uploaded_by) != current_user.user_id and not current_user.is_admin:
        #         raise HTTPException(status_code=403, detail="Access denied")
        # 
        # file_path = Path(uploaded_file.file_path)
        # if not file_path.exists():
        #     raise HTTPException(status_code=404, detail="File not found on disk")
        # 
        # # Update download count
        # await database.files.update_one(
        #     {"_id": ObjectId(file_id)},
        #     {"$inc": {"download_count": 1}}
        # )
        # 
        # return FileResponse(
        #     path=str(file_path),
        #     filename=uploaded_file.original_filename,
        #     media_type=uploaded_file.content_type
        # )
        
        # For demo purposes, return error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File serving not implemented in demo mode"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a file"""
    
    try:
        # TODO: Get file info and check permissions
        # database = await get_database()
        # file_doc = await database.files.find_one({"_id": ObjectId(file_id)})
        # if not file_doc:
        #     raise HTTPException(status_code=404, detail="File not found")
        # 
        # uploaded_file = UploadedFile(**file_doc)
        # 
        # # Check permissions (owner or admin)
        # if str(uploaded_file.uploaded_by) != current_user.user_id and not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="Access denied")
        # 
        # # Delete file from disk
        # file_path = Path(uploaded_file.file_path)
        # if file_path.exists():
        #     file_path.unlink()
        # 
        # # Delete from database
        # await database.files.delete_one({"_id": ObjectId(file_id)})
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "file_id": file_id,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )


@router.get("/")
async def list_user_files(
    limit: int = 20,
    skip: int = 0,
    file_type: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """List user's uploaded files"""
    
    try:
        # TODO: Get files from database
        # database = await get_database()
        # 
        # query_filter = {"uploaded_by": ObjectId(current_user.user_id)}
        # if file_type:
        #     query_filter["content_type"] = {"$regex": file_type, "$options": "i"}
        # 
        # cursor = database.files.find(query_filter).sort([
        #     ("created_at", -1)
        # ]).skip(skip).limit(limit)
        # 
        # files = await cursor.to_list(length=limit)
        # total = await database.files.count_documents(query_filter)
        
        # For demo purposes, return mock data
        mock_files = [
            {
                "file_id": "file_abc123",
                "filename": "product_image.jpg",
                "original_filename": "my_product.jpg",
                "content_type": "image/jpeg",
                "size": 245760,
                "created_at": datetime.utcnow(),
                "download_count": 5,
                "is_public": False,
                "url": "/api/files/file_abc123"
            },
            {
                "file_id": "file_def456", 
                "filename": "analysis_report.pdf",
                "original_filename": "eco_report.pdf",
                "content_type": "application/pdf",
                "size": 1048576,
                "created_at": datetime.utcnow(),
                "download_count": 12,
                "is_public": True,
                "url": "/api/files/file_def456"
            }
        ]
        
        return {
            "files": mock_files[skip:skip + limit],
            "total": len(mock_files),
            "page": skip // limit + 1,
            "page_size": len(mock_files[skip:skip + limit]),
            "has_more": skip + limit < len(mock_files)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )
