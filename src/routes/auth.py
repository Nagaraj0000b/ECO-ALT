from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from typing import Dict, Any
import motor.motor_asyncio
import os

from ..models.user import (
    UserCreate, UserLogin, UserResponse, PasswordReset, 
    PasswordResetConfirm, TokenData, User
)
from ..utils.auth import AuthUtils
from ..middleware.auth import get_current_user
from bson import ObjectId


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Database connection (will be injected in main app)
async def get_database():
    # This will be properly implemented when we set up the main app
    pass


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
    
    # TODO: Get database connection
    # database = await get_database()
    # 
    # # Check if user already exists
    # existing_user = await database.users.find_one({
    #     "$or": [
    #         {"email": user_data.email},
    #         {"username": user_data.username}
    #     ]
    # })
    # if existing_user:
    #     field = "email" if existing_user.get("email") == user_data.email else "username"
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail=f"User with this {field} already exists"
    #     )
    
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
    
    # TODO: Save to database
    # result = await database.users.insert_one(user.dict(by_alias=True, exclude={"id"}))
    # user.id = result.inserted_id
    
    # TODO: Send verification email
    # await send_verification_email(user.email, user.verification_token)
    
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
    
    # TODO: Get database connection and find user
    # database = await get_database()
    # user_doc = await database.users.find_one({"email": login_data.email})
    # if not user_doc:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid email or password"
    #     )
    
    # user = User(**user_doc)
    
    # For demo purposes, create a mock user
    user = User(
        username="demo_user",
        email=login_data.email,
        password_hash=AuthUtils.hash_password("password123"),
        first_name="Demo",
        last_name="User",
        is_active=True,
        is_admin=False
    )
    
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
        
        # TODO: Update user in database
        # await database.users.update_one(
        #     {"_id": user.id},
        #     {"$set": {"login_attempts": user.login_attempts, "locked_until": user.locked_until}}
        # )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Reset login attempts on successful login
    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    
    # TODO: Update user in database
    # await database.users.update_one(
    #     {"_id": user.id},
    #     {"$set": {
    #         "login_attempts": 0,
    #         "locked_until": None,
    #         "last_login": user.last_login
    #     }}
    # )
    
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


@router.post("/logout", response_model=Dict[str, str])
async def logout_user(current_user: TokenData = Depends(get_current_user)):
    """Logout user (invalidate token - for production, implement token blacklisting)"""
    
    # TODO: In production, add token to blacklist in Redis/Database
    # await add_token_to_blacklist(current_user.token)
    
    return {
        "success": True,
        "message": "Successfully logged out"
    }


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    
    try:
        payload = AuthUtils.verify_token(refresh_token, "refresh")
        
        # TODO: Verify user still exists and is active
        # database = await get_database()
        # user = await database.users.find_one({"_id": ObjectId(payload["user_id"])})
        # if not user or not user.get("is_active"):
        #     raise HTTPException(status_code=401, detail="User no longer active")
        
        # Create new access token
        token_data = {
            "user_id": payload["user_id"],
            "username": payload["username"],
            "email": payload["email"],
            "is_admin": payload.get("is_admin", False),
            "subscription_tier": payload.get("subscription_tier", "free")
        }
        
        new_access_token = AuthUtils.create_access_token(token_data)
        
        return {
            "success": True,
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/forgot-password", response_model=Dict[str, str])
async def forgot_password(password_reset: PasswordReset):
    """Request password reset"""
    
    # TODO: Get database connection
    # database = await get_database()
    # user = await database.users.find_one({"email": password_reset.email})
    # if not user:
    #     # Don't reveal whether email exists or not
    #     return {"success": True, "message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = AuthUtils.generate_password_reset_token()
    reset_expires = datetime.utcnow() + timedelta(minutes=AuthUtils.PASSWORD_RESET_EXPIRE_MINUTES)
    
    # TODO: Update user with reset token
    # await database.users.update_one(
    #     {"email": password_reset.email},
    #     {"$set": {
    #         "password_reset_token": reset_token,
    #         "password_reset_expires": reset_expires
    #     }}
    # )
    
    # TODO: Send password reset email
    # await send_password_reset_email(password_reset.email, reset_token)
    
    return {
        "success": True,
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/reset-password", response_model=Dict[str, str])
async def reset_password(reset_data: PasswordResetConfirm):
    """Reset password using token"""
    
    # Check password strength
    is_strong, message = AuthUtils.is_password_strong(reset_data.new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # TODO: Get database connection
    # database = await get_database()
    # user = await database.users.find_one({
    #     "password_reset_token": reset_data.token,
    #     "password_reset_expires": {"$gt": datetime.utcnow()}
    # })
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid or expired reset token"
    #     )
    
    # Hash new password
    new_password_hash = AuthUtils.hash_password(reset_data.new_password)
    
    # TODO: Update user password and clear reset token
    # await database.users.update_one(
    #     {"_id": user["_id"]},
    #     {"$set": {
    #         "password_hash": new_password_hash,
    #         "password_reset_token": None,
    #         "password_reset_expires": None,
    #         "login_attempts": 0,
    #         "locked_until": None,
    #         "updated_at": datetime.utcnow()
    #     }}
    # )
    
    return {
        "success": True,
        "message": "Password has been reset successfully"
    }


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user profile"""
    
    # TODO: Get full user data from database
    # database = await get_database()
    # user_doc = await database.users.find_one({"_id": ObjectId(current_user.user_id)})
    # if not user_doc:
    #     raise HTTPException(status_code=404, detail="User not found")
    # user = User(**user_doc)
    
    # For demo purposes, return mock user
    user = User(
        username=current_user.username,
        email=current_user.email,
        password_hash="",
        first_name="Demo",
        last_name="User",
        is_active=True,
        is_admin=current_user.is_admin
    )
    user.id = ObjectId(current_user.user_id) if current_user.user_id else ObjectId()
    
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
