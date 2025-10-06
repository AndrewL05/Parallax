from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
import logging

from models.user import User, UserCreate, UserUpdate
from database import get_database
from auth import get_current_user, verify_clerk_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/sync")
async def sync_user_profile(
    user_data: dict,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Sync user profile from Clerk to MongoDB"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db = await get_database()
    clerk_id = current_user.get("clerk_id")
    
    user_doc = {
        "clerk_id": clerk_id,
        "email": user_data.get("email"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "last_login": datetime.utcnow()
    }
    
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