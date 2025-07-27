from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
import json
import re
from datetime import datetime

from ..models.simulation import SimulationRequest, Simulation, SimulationResult, TimelinePoint
from ..database import get_database
from ..auth import get_current_user
from ..services.ai_service import generate_life_simulation

logger = logging.getLogger(__name__)
router = APIRouter(tags=["simulation"])

@router.post("/simulate", response_model=SimulationResult)
async def create_life_simulation(
    request: SimulationRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Generate AI-powered life simulation comparing two choices"""
    db = await get_database()
    user_id = current_user.get("id") if current_user else None
    
    # Check if user has premium access for advanced simulations
    if current_user:
        user_doc = await db.users.find_one({"clerk_id": current_user["clerk_id"]})
        if user_doc and user_doc.get("subscription_tier") == "free":
            # Check simulation count for free users (limit to 3 per month)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            simulation_count = await db.simulations.count_documents({
                "user_id": str(user_doc.get("_id")),
                "created_at": {"$gte": thirty_days_ago}
            })
            
            if simulation_count >= 3:
                raise HTTPException(
                    status_code=403, 
                    detail="Free tier limit reached. Upgrade to Premium for unlimited simulations."
                )
    
    try:
        # Generate AI simulation
        ai_data = await generate_life_simulation(request)
        
        # Create simulation object
        simulation = Simulation(
            user_id=str(user_id) if user_id else None,
            choice_a=request.choice_a,
            choice_b=request.choice_b,
            user_context=request.user_context,
            choice_a_timeline=[TimelinePoint(**point) for point in ai_data["choice_a_timeline"]],
            choice_b_timeline=[TimelinePoint(**point) for point in ai_data["choice_b_timeline"]],
            summary=ai_data.get("summary", "Simulation completed successfully.")
        )
        
        # Save to database
        simulation_dict = simulation.dict()
        result = await db.simulations.insert_one(simulation_dict)
        simulation_dict["_id"] = str(result.inserted_id)
        
        logger.info(f"Simulation created with ID: {simulation.id}")
        
        # Return result
        return SimulationResult(
            id=simulation.id,
            choice_a_timeline=simulation.choice_a_timeline,
            choice_b_timeline=simulation.choice_b_timeline,
            summary=simulation.summary,
            created_at=simulation.created_at
        )
        
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate simulation: {str(e)}")

@router.get("/simulations", response_model=List[SimulationResult])
async def get_user_simulations(current_user: dict = Depends(get_current_user)):
    """Get all simulations for the authenticated user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db = await get_database()
    user_doc = await db.users.find_one({"clerk_id": current_user["clerk_id"]})
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    simulations = await db.simulations.find(
        {"user_id": str(user_doc["_id"])}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    return [
        SimulationResult(
            id=sim["id"],
            choice_a_timeline=[TimelinePoint(**point) for point in sim["choice_a_timeline"]],
            choice_b_timeline=[TimelinePoint(**point) for point in sim["choice_b_timeline"]],
            summary=sim["summary"],
            created_at=sim["created_at"]
        )
        for sim in simulations
    ]

@router.get("/simulation/{simulation_id}")
async def get_simulation(
    simulation_id: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a specific simulation by ID"""
    db = await get_database()
    
    # Find simulation
    simulation = await db.simulations.find_one({"id": simulation_id})
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Check access permissions
    if simulation.get("user_id") and current_user:
        user_doc = await db.users.find_one({"clerk_id": current_user["clerk_id"]})
        if not user_doc or str(user_doc["_id"]) != simulation["user_id"]:
            if not simulation.get("is_public", False):
                raise HTTPException(status_code=403, detail="Access denied")
    elif simulation.get("user_id") and not current_user:
        if not simulation.get("is_public", False):
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Convert ObjectId to string
    if "_id" in simulation:
        simulation["_id"] = str(simulation["_id"])
    
    return simulation