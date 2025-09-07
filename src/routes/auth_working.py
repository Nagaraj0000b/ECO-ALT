from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import motor.motor_asyncio
import os

from ..models.user import (
    UserCreate, UserLogin, UserResponse, PasswordReset, 
    PasswordResetConfirm, TokenData, User, UserUpdate
)
from ..utils.auth import AuthUtils
from ..middleware.auth import get_current_user
from bson import ObjectId


router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Database connection
def get_database():
    """Get MongoDB database connection"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("MONGODB_DATABASE", "eco_products")
    
    client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
    return client[database_name]


@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate):
    """Register a new user account"""
    
    # Check password strength
    is_strong, message = AuthUtils.is_password_strong(user_data.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Get database connection
    database = get_database()
    
    # Check if user already exists
    existing_user = await database.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    if existing_user:
        field = "email" if existing_user.get("email") == user_data.email else "username"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with this {field} already exists"
        )
    
    # Hash password
    password_hash = AuthUtils.hash_password(user_data.password)
    
    # Create user object
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        verification_token=AuthUtils.generate_verification_token(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to database
    try:
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        print(f"DEBUG: Attempting to save user: {user_dict.get('email')}")
        result = await database.users.insert_one(user_dict)
        user.id = result.inserted_id
        print(f"DEBUG: User saved with ID: {user.id}")
    except Exception as e:
        print(f"ERROR: Failed to save user to database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account: {str(e)}"
        )
    
    # Create tokens
    token_data = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "subscription_tier": user.subscription_tier
    }
    
    access_token = AuthUtils.create_access_token(token_data)
    refresh_token = AuthUtils.create_refresh_token(token_data)
    
    return {
        "success": True,
        "message": "User registered successfully. Please check your email for verification.",
        "user": UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            is_verified=user.is_verified,
            profile=user.profile,
            created_at=user.created_at,
            last_login=user.last_login,
            api_calls_count=user.api_calls_count,
            subscription_tier=user.subscription_tier
        ),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """Login user and return tokens"""
    
    # Get database connection and find user
    database = get_database()
    user_doc = await database.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Convert to User object
    user = User(**user_doc)
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to too many failed login attempts"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Verify password
    if not AuthUtils.verify_password(login_data.password, user.password_hash):
        # Increment login attempts
        user.login_attempts += 1
        if user.login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        # Update user in database
        await database.users.update_one(
            {"_id": user.id},
            {"$set": {"login_attempts": user.login_attempts, "locked_until": user.locked_until}}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Reset login attempts on successful login
    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    
    # Update user in database
    await database.users.update_one(
        {"_id": user.id},
        {"$set": {
            "login_attempts": 0,
            "locked_until": None,
            "last_login": user.last_login
        }}
    )
    
    # Create tokens
    token_data = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "subscription_tier": user.subscription_tier
    }
    
    access_token = AuthUtils.create_access_token(token_data)
    refresh_token = AuthUtils.create_refresh_token(token_data)
    
    return {
        "success": True,
        "message": "Login successful",
        "user": UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            is_verified=user.is_verified,
            profile=user.profile,
            created_at=user.created_at,
            last_login=user.last_login,
            api_calls_count=user.api_calls_count,
            subscription_tier=user.subscription_tier
        ),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user profile"""
    
    database = get_database()
    user_doc = await database.users.find_one({"_id": ObjectId(current_user.user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_verified=user.is_verified,
        profile=user.profile,
        created_at=user.created_at,
        last_login=user.last_login,
        api_calls_count=user.api_calls_count,
        subscription_tier=user.subscription_tier
    )


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(refresh_data: Dict[str, str]):
    """Refresh access token using refresh token"""
    
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    try:
        # Verify refresh token
        payload = AuthUtils.verify_token(refresh_token, "refresh")
        
        # Create new access token
        token_data = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "is_admin": payload.get("is_admin", False),
            "subscription_tier": payload.get("subscription_tier", "free")
        }
        
        new_access_token = AuthUtils.create_access_token(token_data)
        
        return {
            "success": True,
            "access_token": new_access_token,
            "token_type": "bearer",
            "message": "Token refreshed successfully"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update user profile information"""
    
    try:
        database = get_database()
        
        # Build update data
        update_data = {}
        if profile_data.first_name is not None:
            update_data["first_name"] = profile_data.first_name
        if profile_data.last_name is not None:
            update_data["last_name"] = profile_data.last_name
        if profile_data.profile is not None:
            update_data["profile"] = profile_data.profile.model_dump()
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update user in database
        result = await database.users.update_one(
            {"_id": ObjectId(current_user.user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user_doc = await database.users.find_one({"_id": ObjectId(current_user.user_id)})
        updated_user = User(**updated_user_doc)
        
        return UserResponse(
            id=str(updated_user.id),
            username=updated_user.username,
            email=updated_user.email,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            is_active=updated_user.is_active,
            is_admin=updated_user.is_admin,
            is_verified=updated_user.is_verified,
            profile=updated_user.profile,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login,
            api_calls_count=updated_user.api_calls_count,
            subscription_tier=updated_user.subscription_tier
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )


@router.post("/logout", response_model=Dict[str, str])
async def logout_user(current_user: TokenData = Depends(get_current_user)):
    """Logout user (invalidate token - for production, implement token blacklisting)"""
    
    # TODO: In production, add token to blacklist in Redis/Database
    # await add_token_to_blacklist(current_user.token)
    
    return {
        "success": "true",
        "message": "Logout successful"
    }


@router.post("/change-password", response_model=Dict[str, str])
async def change_password(
    password_data: Dict[str, str],
    current_user: TokenData = Depends(get_current_user)
):
    """Change user password"""
    
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both current_password and new_password are required"
        )
    
    # Check new password strength
    is_strong, message = AuthUtils.is_password_strong(new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Get user from database
    database = get_database()
    user_doc = await database.users.find_one({"_id": ObjectId(current_user.user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    
    # Verify current password
    if not AuthUtils.verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password and update
    new_password_hash = AuthUtils.hash_password(new_password)
    await database.users.update_one(
        {"_id": ObjectId(current_user.user_id)},
        {"$set": {
            "password_hash": new_password_hash,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "success": "true",
        "message": "Password changed successfully"
    }
