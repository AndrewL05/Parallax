from fastapi import HTTPException, Depends
from typing import Optional, Callable
from functools import wraps
import logging

from auth import get_current_user
from services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class PremiumRequired(Exception):
    """Custom exception for premium feature access"""
    def __init__(self, message: str, feature: str, tier: str):
        self.message = message
        self.feature = feature
        self.tier = tier
        super().__init__(self.message)

async def require_premium_subscription(
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Dependency that requires premium subscription"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for premium features"
        )

    user_id = current_user.get("id") or current_user.get("clerk_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user session"
        )

    subscription = await SubscriptionService.get_user_subscription(user_id)

    if not subscription.has_premium_access():
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "This feature requires a premium subscription",
                "current_tier": subscription.tier,
                "required_tier": "premium",
                "subscription_status": subscription.status
            }
        )

    return current_user

async def require_feature_access(
    feature: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Dependency factory for specific feature access control"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    user_id = current_user.get("id") or current_user.get("clerk_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user session"
        )

    access_check = await SubscriptionService.check_usage_limits(user_id, feature)

    if not access_check["allowed"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_access_denied",
                "message": access_check["reason"],
                "feature": feature,
                "tier": access_check["tier"],
                "usage_info": access_check.get("usage_info", {})
            }
        )

    return current_user

def premium_feature(feature_name: str):
    """Decorator for premium feature endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs if it exists
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            user_id = current_user.get("id") or current_user.get("clerk_id")
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid user session"
                )

            access_check = await SubscriptionService.check_usage_limits(user_id, feature_name)

            if not access_check["allowed"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "feature_access_denied",
                        "message": access_check["reason"],
                        "feature": feature_name,
                        "tier": access_check["tier"],
                        "usage_info": access_check.get("usage_info", {})
                    }
                )

            # Record usage after successful access check
            try:
                result = await func(*args, **kwargs)
                await SubscriptionService.record_usage(user_id, feature_name)
                return result
            except Exception as e:
                logger.error(f"Error in premium feature {feature_name}: {e}")
                raise

        return wrapper
    return decorator

def usage_limited(feature_name: str):
    """Decorator for usage-limited features"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            user_id = current_user.get("id") or current_user.get("clerk_id")
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid user session"
                )

            access_check = await SubscriptionService.check_usage_limits(user_id, feature_name)

            if not access_check["allowed"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "usage_limit_exceeded",
                        "message": access_check["reason"],
                        "feature": feature_name,
                        "tier": access_check["tier"],
                        "usage_info": access_check.get("usage_info", {}),
                        "upgrade_required": True
                    }
                )

            try:
                result = await func(*args, **kwargs)
                await SubscriptionService.record_usage(user_id, feature_name)
                return result
            except Exception as e:
                logger.error(f"Error in usage-limited feature {feature_name}: {e}")
                raise

        return wrapper
    return decorator

# Specific dependency functions for common features
async def require_simulation_access(
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Dependency for simulation access with usage limits"""
    return await require_feature_access("simulation", current_user)

async def require_advanced_simulation_access(
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Dependency for advanced simulation features"""
    return await require_feature_access("advanced_simulation", current_user)

async def require_ai_chatbot_access(
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Dependency for AI chatbot access"""
    return await require_feature_access("ai_chatbot", current_user)

async def require_custom_scenario_access(
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Dependency for custom scenario creation"""
    return await require_feature_access("custom_scenarios", current_user)

async def require_risk_assessment_access(
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Dependency for risk assessment access with usage limits"""
    return await require_feature_access("risk_assessment", current_user)

# Utility functions for checking access without raising exceptions
async def check_premium_access(user_id: str) -> bool:
    """Check if user has premium access without raising exceptions"""
    try:
        subscription = await SubscriptionService.get_user_subscription(user_id)
        return subscription.has_premium_access()
    except Exception as e:
        logger.error(f"Error checking premium access for user {user_id}: {e}")
        return False

async def check_feature_access(user_id: str, feature: str) -> dict:
    """Check feature access and return detailed information"""
    try:
        return await SubscriptionService.check_usage_limits(user_id, feature)
    except Exception as e:
        logger.error(f"Error checking feature access for user {user_id}, feature {feature}: {e}")
        return {
            "allowed": False,
            "reason": "Error checking access",
            "tier": "unknown"
        }