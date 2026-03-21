import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from database import db
from models.simulation import (
    SimulationRequest,
    LifeChoice,
    UserContext,
    Simulation,
    TimelinePoint,
)
from services.ai_service import generate_life_simulation

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEMO_REQUEST = SimulationRequest(
    choice_a=LifeChoice(
        title="Physician",
        description="Pursue a career in medicine — residency, fellowship, and clinical practice.",
        category="career",
    ),
    choice_b=LifeChoice(
        title="Lawyer",
        description="Attend law school, pass the bar, and build a legal career.",
        category="career",
    ),
    user_context=UserContext(
        age="22",
        current_location="New York, NY",
        current_salary="0",
        education_level="bachelor",
    ),
)


async def seed() -> None:
    deleted = await db.simulations.delete_many({"is_demo": True})
    if deleted.deleted_count:
        logger.info(f"Removed {deleted.deleted_count} previous demo simulation(s)")

    logger.info("Generating demo simulation (Physician vs Lawyer) via ML + AI pipeline...")
    ai_data = await generate_life_simulation(DEMO_REQUEST)

    simulation = Simulation(
        user_id=None,
        choice_a=DEMO_REQUEST.choice_a,
        choice_b=DEMO_REQUEST.choice_b,
        user_context=DEMO_REQUEST.user_context or UserContext(),
        choice_a_timeline=[TimelinePoint(**p) for p in ai_data["choice_a_timeline"]],
        choice_b_timeline=[TimelinePoint(**p) for p in ai_data["choice_b_timeline"]],
        summary=ai_data.get("summary", "Simulation completed successfully."),
        is_public=True,
    )

    doc = simulation.dict()
    doc["is_demo"] = True

    await db.simulations.insert_one(doc)
    logger.info(f"Demo simulation seeded (id={simulation.id})")


if __name__ == "__main__":
    asyncio.run(seed())
