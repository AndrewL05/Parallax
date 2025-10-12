"""
ML Scenarios API Routes
FastAPI endpoints for ML-powered scenario generation and predictions.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Literal
import os
import sys
from pathlib import Path

ml_dir = Path(__file__).parent.parent / "ml"
sys.path.insert(0, str(ml_dir))

from scenario_service import ScenarioService

router = APIRouter(prefix="/api/ml", tags=["ML Scenarios"])

_scenario_service: Optional[ScenarioService] = None


def get_scenario_service() -> ScenarioService:
    global _scenario_service
    if _scenario_service is None:
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        _scenario_service = ScenarioService(
            models_dir=str(ml_dir / "models"),
            features_dir=str(ml_dir / "data" / "features"),
            openrouter_api_key=openrouter_key
        )
    return _scenario_service



class UserProfileRequest(BaseModel):
    age: int = Field(..., ge=18, le=70, description="Current age")
    education: Literal["high_school", "associates", "bachelors", "masters", "phd"] = Field(
        ..., description="Education level"
    )
    field: Literal[
        "technology", "finance", "healthcare", "engineering",
        "education", "business", "creative", "service", "other"
    ] = Field(..., description="Career field")
    experience_years: int = Field(..., ge=0, le=50, description="Years of professional experience")
    current_salary: Optional[float] = Field(None, ge=0, description="Current annual salary (optional)")
    location_type: Literal["urban", "suburban", "rural"] = Field(
        default="urban", description="Location type"
    )
    remote_work: Literal["full", "hybrid", "none"] = Field(
        default="none", description="Remote work status"
    )


class ScenarioRequest(BaseModel):
    """Request for scenario generation."""
    user_profile: UserProfileRequest
    years: int = Field(default=10, ge=1, le=30, description="Number of years to project")
    include_narratives: bool = Field(default=True, description="Include LLM-generated narratives")


class QuickPredictionRequest(BaseModel):
    """Request for quick prediction."""
    user_profile: UserProfileRequest
    target_year: int = Field(default=5, ge=1, le=10, description="Target year for prediction")


# API Endpoints
@router.post("/scenarios/generate")
async def generate_scenarios(request: ScenarioRequest):
    """
    Generate complete life scenarios with ML predictions and narratives.

    Returns optimistic, realistic, and pessimistic scenarios with:
    - 10-year timeline projections
    - Salary growth predictions
    - Life satisfaction scores
    - Career milestones and events
    - Natural language narratives (optional)
    """
    try:
        service = get_scenario_service()

        result = service.generate_complete_scenarios(
            user_profile=request.user_profile.model_dump(),
            years=request.years,
            include_narratives=request.include_narratives
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario generation failed: {str(e)}")


@router.post("/scenarios/single")
async def generate_single_scenario(
    request: ScenarioRequest,
    scenario_type: Literal["optimistic", "realistic", "pessimistic"] = Query(
        default="realistic", description="Type of scenario to generate"
    )
):
    """
    Generate a single scenario (faster than generating all three).

    Returns one scenario with timeline and optional narrative.
    """
    try:
        service = get_scenario_service()

        result = service.generate_single_scenario(
            user_profile=request.user_profile.model_dump(),
            scenario_type=scenario_type,
            years=request.years,
            include_narrative=request.include_narratives
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario generation failed: {str(e)}")


@router.post("/predict/quick")
async def quick_prediction(request: QuickPredictionRequest):
    """
    Generate a quick prediction for a specific future year.

    Returns salary, satisfaction, and career metrics across all scenario types
    for the target year.
    """
    try:
        service = get_scenario_service()

        result = service.generate_quick_prediction(
            user_profile=request.user_profile.model_dump(),
            target_year=request.target_year
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/insights/career")
async def get_career_insights(user_profile: UserProfileRequest):
    """
    Get personalized career insights and recommendations.

    Returns:
    - Career stage assessment
    - Growth potential analysis
    - 5-year salary projections
    - Personalized recommendations
    """
    try:
        service = get_scenario_service()

        insights = service.get_career_insights(user_profile.model_dump())

        return {
            "success": True,
            "data": insights
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for ML service.

    Returns service status and model availability.
    """
    try:
        service = get_scenario_service()

        return {
            "status": "healthy",
            "ml_service": "operational",
            "model_loaded": service.simulator.model is not None,
            "narrative_service": service.narrator.client is not None,
            "version": "1.0.0"
        }

    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


@router.get("/docs/example")
async def get_example_request():
    """
    Get an example request payload for scenario generation.
    """
    return {
        "example_request": {
            "user_profile": {
                "age": 28,
                "education": "bachelors",
                "field": "technology",
                "experience_years": 4,
                "current_salary": 85000,
                "location_type": "urban",
                "remote_work": "hybrid"
            },
            "years": 10,
            "include_narratives": True
        },
        "supported_fields": [
            "technology", "finance", "healthcare", "engineering",
            "education", "business", "creative", "service", "other"
        ],
        "supported_education_levels": [
            "high_school", "associates", "bachelors", "masters", "phd"
        ],
        "notes": [
            "current_salary is optional - will be estimated if not provided",
            "years can be 1-30, default is 10",
            "narratives require OPENROUTER_API_KEY environment variable"
        ]
    }
