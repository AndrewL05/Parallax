from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from io import BytesIO
import json

from models.simulation import SimulationResult, TimelinePoint
from models.subscription import SubscriptionTier
from database import get_database
from auth import get_current_user
from services.subscription_service import SubscriptionService
from middleware.premium_auth import (
    require_premium_subscription,
    require_advanced_simulation_access,
    require_custom_scenario_access,
    require_risk_assessment_access,
    premium_feature,
    usage_limited
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/premium", tags=["premium"])

@router.get("/subscription/status")
async def get_subscription_status(
    current_user: dict = Depends(get_current_user)
):
    """Get detailed subscription status and analytics"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("clerk_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user data")

    analytics = await SubscriptionService.get_subscription_analytics(user_id)

    return analytics

@router.post("/simulations/advanced")
@premium_feature("advanced_simulation")
async def create_advanced_simulation(
    request: Dict[str, Any],
    current_user: dict = Depends(require_advanced_simulation_access)
):
    """Create advanced simulation with premium features"""
    # Enhanced simulation logic with premium features
    enhanced_request = {
        **request,
        "advanced_features": {
            "detailed_analysis": True,
            "market_conditions": True,
            "psychological_factors": True,
            "monte_carlo_analysis": True,
            "extended_timeline": True,
            "scenario_variations": True
        }
    }

    # This would integrate with enhanced AI service
    logger.info(f"Creating advanced simulation for user {current_user.get('clerk_id')}")

    return {
        "message": "Advanced simulation created",
        "features_included": enhanced_request["advanced_features"],
        "simulation_id": "advanced_" + str(datetime.utcnow().timestamp())
    }

@router.post("/simulations/risk-assessment")
@usage_limited("risk_assessment")
async def create_risk_assessment(
    request: Dict[str, Any],
    current_user: dict = Depends(require_risk_assessment_access)
):
    """Create risk assessment for simulation (3 per week for free users)"""
    # Risk assessment logic
    assessment_request = {
        **request,
        "risk_features": {
            "financial_risk": True,
            "career_risk": True,
            "personal_risk": True,
            "market_volatility": True,
            "timeline_risks": True
        }
    }

    logger.info(f"Creating risk assessment for user {current_user.get('clerk_id')}")

    return {
        "message": "Risk assessment created",
        "assessment_id": "risk_" + str(datetime.utcnow().timestamp()),
        "risk_factors_analyzed": assessment_request["risk_features"],
        "confidence_score": 0.85  # Example confidence score
    }

@router.post("/scenarios/custom")
@premium_feature("custom_scenarios")
async def create_custom_scenario(
    scenario_data: Dict[str, Any],
    current_user: dict = Depends(require_custom_scenario_access)
):
    """Create custom simulation scenarios (premium feature)"""
    db = await get_database()
    user_id = current_user.get("clerk_id")

    custom_scenario = {
        "id": f"custom_{datetime.utcnow().timestamp()}",
        "user_id": user_id,
        "title": scenario_data.get("title"),
        "description": scenario_data.get("description"),
        "parameters": scenario_data.get("parameters", {}),
        "category": "custom",
        "created_at": datetime.utcnow(),
        "is_public": scenario_data.get("is_public", False)
    }

    await db.custom_scenarios.insert_one(custom_scenario)

    logger.info(f"Created custom scenario for user {user_id}")

    return {
        "scenario_id": custom_scenario["id"],
        "message": "Custom scenario created successfully"
    }

@router.get("/scenarios/custom")
async def get_custom_scenarios(
    current_user: dict = Depends(require_custom_scenario_access)
):
    """Get user's custom scenarios"""
    db = await get_database()
    user_id = current_user.get("clerk_id")

    scenarios = await db.custom_scenarios.find({
        "$or": [
            {"user_id": user_id},
            {"is_public": True}
        ]
    }).sort("created_at", -1).to_list(100)

    # Convert ObjectId to string
    for scenario in scenarios:
        if "_id" in scenario:
            scenario["_id"] = str(scenario["_id"])

    return scenarios

@router.get("/simulations/export")
async def export_simulations(
    format: str = Query(..., regex="^(json|pdf|csv|excel)$"),
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(require_premium_subscription)
):
    """Export simulation data in various formats (premium feature)"""
    db = await get_database()
    user_doc = await db.users.find_one({"clerk_id": current_user["clerk_id"]})

    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user has access to this export format
    subscription = await SubscriptionService.get_user_subscription(current_user.get("clerk_id"))
    from models.subscription import TIER_LIMITS
    allowed_formats = TIER_LIMITS[subscription.tier].export_formats

    if format not in allowed_formats:
        raise HTTPException(
            status_code=403,
            detail=f"Export format '{format}' not available in {subscription.tier} tier"
        )

    # Get user simulations
    simulations = await db.simulations.find(
        {"user_id": str(user_doc["_id"])}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    if format == "json":
        # Convert ObjectId to string for JSON serialization
        for sim in simulations:
            if "_id" in sim:
                sim["_id"] = str(sim["_id"])

        return {
            "format": "json",
            "count": len(simulations),
            "data": simulations,
            "exported_at": datetime.utcnow()
        }

    elif format == "csv":
        # Simplified CSV export - in production you'd use pandas or csv module
        csv_data = "id,choice_a_title,choice_b_title,created_at,summary\n"
        for sim in simulations:
            csv_data += f"{sim['id']},{sim['choice_a']['title']},{sim['choice_b']['title']},{sim['created_at']},{sim['summary']}\n"

        return {
            "format": "csv",
            "count": len(simulations),
            "data": csv_data,
            "exported_at": datetime.utcnow()
        }

    else:
        # For PDF and Excel, you'd implement proper generation
        return {
            "format": format,
            "message": f"{format.upper()} export will be available soon",
            "count": len(simulations),
            "exported_at": datetime.utcnow()
        }

@router.get("/analytics/dashboard")
async def get_premium_analytics(
    period_days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(require_premium_subscription)
):
    """Get premium analytics dashboard data"""
    db = await get_database()
    user_doc = await db.users.find_one({"clerk_id": current_user["clerk_id"]})

    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = str(user_doc["_id"])
    start_date = datetime.utcnow() - timedelta(days=period_days)

    # Get simulation statistics
    simulations = await db.simulations.find({
        "user_id": user_id,
        "created_at": {"$gte": start_date}
    }).to_list(1000)

    # Calculate analytics
    analytics = {
        "period_days": period_days,
        "total_simulations": len(simulations),
        "simulations_by_category": {},
        "average_happiness_scores": {},
        "decision_patterns": {},
        "timeline": []
    }

    # Process simulations for insights
    for sim in simulations:
        # Category analysis
        cat_a = sim["choice_a"].get("category", "other")
        cat_b = sim["choice_b"].get("category", "other")

        analytics["simulations_by_category"][cat_a] = analytics["simulations_by_category"].get(cat_a, 0) + 1
        analytics["simulations_by_category"][cat_b] = analytics["simulations_by_category"].get(cat_b, 0) + 1

        # Happiness score analysis
        if sim.get("choice_a_timeline"):
            avg_happiness_a = sum(point.get("happiness_score", 0) for point in sim["choice_a_timeline"]) / len(sim["choice_a_timeline"])
            analytics["average_happiness_scores"][sim["choice_a"]["title"]] = avg_happiness_a

        if sim.get("choice_b_timeline"):
            avg_happiness_b = sum(point.get("happiness_score", 0) for point in sim["choice_b_timeline"]) / len(sim["choice_b_timeline"])
            analytics["average_happiness_scores"][sim["choice_b"]["title"]] = avg_happiness_b

    return analytics

@router.get("/support/priority")
async def get_priority_support_info(
    current_user: dict = Depends(require_premium_subscription)
):
    """Get priority support information for premium users"""
    return {
        "support_tier": "priority",
        "response_time": "Within 2 hours during business hours",
        "channels": ["email", "chat", "phone"],
        "dedicated_support": True,
        "contact_info": {
            "email": "premium-support@parallax.com",
            "chat": "Available in dashboard",
            "phone": "+1-555-PREMIUM"
        },
        "features": [
            "Priority ticket handling",
            "Direct access to senior support team",
            "Video call support available",
            "Custom integration assistance"
        ]
    }

@router.post("/feedback/premium")
async def submit_premium_feedback(
    feedback_data: Dict[str, Any],
    current_user: dict = Depends(require_premium_subscription)
):
    """Submit feedback specifically for premium features"""
    db = await get_database()

    feedback = {
        "id": f"feedback_{datetime.utcnow().timestamp()}",
        "user_id": current_user.get("clerk_id"),
        "type": "premium_feedback",
        "category": feedback_data.get("category"),
        "message": feedback_data.get("message"),
        "rating": feedback_data.get("rating"),
        "feature": feedback_data.get("feature"),
        "created_at": datetime.utcnow(),
        "priority": "high"  # Premium feedback gets high priority
    }

    await db.feedback.insert_one(feedback)

    return {
        "message": "Premium feedback submitted successfully",
        "feedback_id": feedback["id"],
        "priority": "high"
    }