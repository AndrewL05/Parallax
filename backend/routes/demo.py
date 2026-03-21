from fastapi import APIRouter, HTTPException
import logging

from database import get_database
from models.simulation import SimulationResult, TimelinePoint

logger = logging.getLogger(__name__)
router = APIRouter(tags=["demo"])


@router.get("/demo/simulation", response_model=SimulationResult)
async def get_demo_simulation():
    # Return the seeded demo simulation
    db = await get_database()
    doc = await db.simulations.find_one({"is_demo": True})

    if not doc:
        raise HTTPException(status_code=404, detail="Demo simulation not found. Run: python -m scripts.seed_demo")

    return SimulationResult(
        id=doc["id"],
        choice_a_timeline=[TimelinePoint(**p) for p in doc["choice_a_timeline"]],
        choice_b_timeline=[TimelinePoint(**p) for p in doc["choice_b_timeline"]],
        summary=doc["summary"],
        created_at=doc["created_at"],
    )
