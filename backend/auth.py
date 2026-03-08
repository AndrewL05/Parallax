from fastapi import HTTPException, Header
from typing import Optional
import logging
import jwt
import requests
import os
import time

logger = logging.getLogger(__name__)

# Cache JWKS keys to avoid fetching on every request
_jwks_cache = {"keys": None, "fetched_at": 0}
_JWKS_CACHE_TTL = 3600  # Re-fetch JWKS every hour


def _get_jwks_keys(jwks_url: str) -> dict:
    """Fetch and cache JWKS keys from Clerk."""
    now = time.time()
    if _jwks_cache["keys"] and (now - _jwks_cache["fetched_at"]) < _JWKS_CACHE_TTL:
        return _jwks_cache["keys"]

    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        jwks_data = response.json()
        _jwks_cache["keys"] = jwks_data
        _jwks_cache["fetched_at"] = now
        logger.info("JWKS keys fetched and cached successfully")
        return jwks_data
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS keys: {e}")
        # Return cached keys if available, even if stale
        if _jwks_cache["keys"]:
            logger.warning("Using stale JWKS cache")
            return _jwks_cache["keys"]
        raise HTTPException(status_code=500, detail="Failed to fetch authentication keys")


def _get_signing_key(jwks_data: dict, token: str):
    """Extract the correct signing key from JWKS for the given token."""
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks_data.get("keys", []):
        if key.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)

    raise HTTPException(status_code=401, detail="Unable to find matching signing key")


async def verify_clerk_token(authorization: str):
    """Verify Clerk JWT token with full signature validation."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split(" ")[1]

    try:
        jwks_url = os.environ.get('CLERK_JWKS_URL')
        if not jwks_url:
            raise HTTPException(status_code=500, detail="Clerk JWKS URL not configured")

        # Fetch JWKS and get the correct signing key
        jwks_data = _get_jwks_keys(jwks_url)
        signing_key = _get_signing_key(jwks_data, token)

        # Decode WITH full signature verification
        decoded = jwt.decode(
            token,
            key=signing_key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,  # Clerk tokens may not have aud
            },
        )
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
    except HTTPException:
        raise
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