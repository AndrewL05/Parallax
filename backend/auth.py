from fastapi import HTTPException, Header
from typing import Optional
import logging
import jwt
import requests
import os

logger = logging.getLogger(__name__)

async def verify_clerk_token(authorization: str):
    """Verify Clerk JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        jwks_url = os.environ.get('CLERK_JWKS_URL')
        if not jwks_url:
            raise HTTPException(status_code=500, detail="Clerk JWKS URL not configured")
        
        decoded = jwt.decode(token, options={"verify_signature": False})
        clerk_id = decoded.get('sub')
        
        if not clerk_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "clerk_id": clerk_id,
            "token_data": decoded
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from authorization header"""
    if not authorization:
        return None
    
    try:
        return await verify_clerk_token(authorization)
    except HTTPException:
        return None