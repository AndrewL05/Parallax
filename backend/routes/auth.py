from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
import logging

from models.user import User, UserCreate, UserUpdate
from database import get_database
from auth import get_current_user, verify_clerk_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

from pydantic import BaseModel
from typing import Union

class UserSyncData(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.post("/sync")
async def sync_user_profile(
    user_data: Union[UserSyncData, dict, str, None] = None,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Sync user profile from Clerk to MongoDB"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db = await get_database()
    clerk_id = current_user.get("clerk_id")
    
    # Handle different input types
    processed_data = {}
    if user_data:
        if isinstance(user_data, str):
            # If it's a JSON string, parse it
            import json
            try:
                processed_data = json.loads(user_data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse user_data as JSON: {user_data}")
                processed_data = {}
        elif isinstance(user_data, UserSyncData):
            # If it's a Pydantic model, convert to dict
            processed_data = user_data.dict()
        elif isinstance(user_data, dict):
            # If it's already a dict, use it
            processed_data = user_data
    
    user_doc = {
        "clerk_id": clerk_id,
        "email": processed_data.get("email"),
        "first_name": processed_data.get("first_name"),
        "last_name": processed_data.get("last_name"),
        "last_login": datetime.utcnow()
    }
    
    # Update or create user
    result = await db.users.update_one(
        {"clerk_id": clerk_id},
        {
            "$set": {**user_doc, "updated_at": datetime.utcnow()},
            "$setOnInsert": {
                "created_at": datetime.utcnow(),
                "subscription_tier": "free",
                "is_active": True
            }
        },
        upsert=True
    )
    
    logger.info(f"User profile synced for clerk_id: {clerk_id}")
    return {"message": "Profile synced successfully"}

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db = await get_database()
    user = await db.users.find_one({"clerk_id": current_user["clerk_id"]})
    
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # Convert ObjectId to string if present
    if "_id" in user:
        user["_id"] = str(user["_id"])
    
    return user

@router.put("/profile")
async def update_user_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db = await get_database()
    clerk_id = current_user["clerk_id"]
    
    # Only update non-None fields
    update_fields = {k: v for k, v in update_data.dict().items() if v is not None}
    if update_fields:
        update_fields["updated_at"] = datetime.utcnow()
        
        result = await db.users.update_one(
            {"clerk_id": clerk_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Profile updated successfully"}