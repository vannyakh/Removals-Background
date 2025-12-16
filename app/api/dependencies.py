"""
API Dependencies
Authentication and common dependencies
"""
from fastapi import Header, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

security = HTTPBearer(auto_error=False)


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> bool:
    """
    Verify API key from X-API-Key header
    
    Args:
        x_api_key: API key from header
        
    Returns:
        True if valid or authentication disabled
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not settings.API_KEY_ENABLED:
        return True
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide X-API-Key header."
        )
    
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True


async def verify_oauth(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> bool:
    """
    Verify OAuth 2.0 token from Authorization header
    
    Args:
        credentials: OAuth credentials from Authorization header
        
    Returns:
        True if valid or authentication disabled
        
    Raises:
        HTTPException: If token is invalid
    """
    if not settings.OAUTH_ENABLED:
        return True
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="OAuth token required. Provide Authorization header with Bearer token."
        )
    
    # TODO: Implement actual OAuth verification
    # For now, just check if token is provided
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid OAuth token"
        )
    
    return True


async def verify_authentication(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> bool:
    """
    Verify authentication (API key or OAuth)
    
    Args:
        x_api_key: API key from X-API-Key header
        credentials: OAuth credentials from Authorization header
        
    Returns:
        True if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    # If neither authentication method is enabled, allow access
    if not settings.API_KEY_ENABLED and not settings.OAUTH_ENABLED:
        return True
    
    # Try API key first
    if settings.API_KEY_ENABLED and x_api_key:
        try:
            await verify_api_key(x_api_key)
            return True
        except HTTPException:
            pass
    
    # Try OAuth
    if settings.OAUTH_ENABLED and credentials:
        try:
            await verify_oauth(credentials)
            return True
        except HTTPException:
            pass
    
    # If we get here and auth is required, raise error
    if settings.API_KEY_ENABLED or settings.OAUTH_ENABLED:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide either X-API-Key header or Authorization Bearer token."
        )
    
    return True

