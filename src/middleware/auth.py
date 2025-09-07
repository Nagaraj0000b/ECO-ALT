from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from ..utils.auth import AuthUtils
from ..models.user import TokenData, User


security = HTTPBearer(auto_error=False)


class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.cleanup_interval = 60  # seconds
        self.last_cleanup = time.time()

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        # Cleanup old requests periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests(now)
            self.last_cleanup = now

        # Get requests for this key
        requests = self.requests[key]
        
        # Remove requests outside the window
        cutoff = now - window
        requests[:] = [req_time for req_time in requests if req_time > cutoff]
        
        # Check if under limit
        if len(requests) >= limit:
            return False
        
        # Add current request
        requests.append(now)
        return True

    def _cleanup_old_requests(self, now: float):
        """Remove old requests from memory"""
        cutoff = now - 3600  # Keep 1 hour of data
        for key in list(self.requests.keys()):
            self.requests[key][:] = [req_time for req_time in self.requests[key] if req_time > cutoff]
            if not self.requests[key]:
                del self.requests[key]


rate_limiter = RateLimiter()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    database=None
) -> Optional[TokenData]:
    """Get current user from JWT token (optional)"""
    if not credentials:
        return None
    
    try:
        payload = AuthUtils.verify_token(credentials.credentials)
        token_data = TokenData(
            user_id=payload.get("user_id"),
            username=payload.get("username"),
            email=payload.get("email"),
            is_admin=payload.get("is_admin", False),
            subscription_tier=payload.get("subscription_tier", "free")
        )
        return token_data
    except HTTPException:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database=None
) -> TokenData:
    """Get current user from JWT token (required)"""
    try:
        payload = AuthUtils.verify_token(credentials.credentials)
        token_data = TokenData(
            user_id=payload.get("user_id"),
            username=payload.get("username"),
            email=payload.get("email"),
            is_admin=payload.get("is_admin", False),
            subscription_tier=payload.get("subscription_tier", "free")
        )
        
        # TODO: Verify user still exists in database
        # user = await database.users.find_one({"_id": ObjectId(token_data.user_id)})
        # if not user or not user.get("is_active", True):
        #     raise HTTPException(status_code=401, detail="User account deactivated")
        
        return token_data
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_admin_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Get client IP
    client_ip = request.client.host
    
    # Different limits for different endpoints
    endpoint = request.url.path
    if endpoint.startswith("/api/auth/"):
        limit, window = 10, 300  # 10 requests per 5 minutes for auth endpoints
    elif endpoint.startswith("/api/analyze"):
        limit, window = 60, 3600  # 60 requests per hour for analysis
    else:
        limit, window = 100, 3600  # 100 requests per hour for other endpoints

    # Check rate limit
    key = f"{client_ip}:{endpoint.split('/')[1] if '/' in endpoint else 'general'}"
    if not rate_limiter.is_allowed(key, limit, window):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {limit} requests per {window} seconds."
        )

    response = await call_next(request)
    return response


class SubscriptionChecker:
    @staticmethod
    def check_api_limit(user: TokenData, endpoint: str) -> bool:
        """Check if user's subscription allows access to endpoint"""
        if user.subscription_tier == "enterprise":
            return True
        elif user.subscription_tier == "premium":
            # Premium users have higher limits
            premium_restricted = ["/api/admin/", "/api/analytics/advanced"]
            return not any(endpoint.startswith(path) for path in premium_restricted)
        else:  # free tier
            free_allowed = [
                "/api/analyze", "/api/search", "/api/health", 
                "/api/auth/", "/api/items", "/api/config"
            ]
            return any(endpoint.startswith(path) for path in free_allowed)

    @staticmethod
    def get_rate_limit(subscription_tier: str) -> tuple[int, int]:
        """Get rate limits based on subscription tier"""
        limits = {
            "free": (20, 3600),      # 20 requests per hour
            "premium": (100, 3600),   # 100 requests per hour
            "enterprise": (1000, 3600)  # 1000 requests per hour
        }
        return limits.get(subscription_tier, limits["free"])


async def subscription_middleware(request: Request, call_next):
    """Check subscription limits"""
    # Skip for public endpoints
    public_endpoints = ["/health", "/docs", "/openapi.json", "/config", "/version"]
    if any(request.url.path.startswith(endpoint) for endpoint in public_endpoints):
        return await call_next(request)

    # Get user from token if present
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = AuthUtils.verify_token(token)
            user_data = TokenData(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                email=payload.get("email"),
                is_admin=payload.get("is_admin", False),
                subscription_tier=payload.get("subscription_tier", "free")
            )
            
            # Check subscription access
            if not SubscriptionChecker.check_api_limit(user_data, request.url.path):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Upgrade subscription to access this feature"
                )
                
        except HTTPException as e:
            # If it's an auth error, let it pass to be handled by auth middleware
            if e.status_code not in [401, 403]:
                raise e

    response = await call_next(request)
    return response
