import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.subscription import (
    Subscription, SubscriptionTier, SubscriptionStatus, BillingPeriod,
    UsageLimit, TIER_LIMITS, UsageTracking
)
from database import get_database

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Service for managing user subscriptions and premium features"""

    @staticmethod
    async def get_user_subscription(user_id: str) -> Optional[Subscription]:
        """Get user's current subscription"""
        db = await get_database()

        subscription_doc = await db.subscriptions.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]  
        )

        if subscription_doc:
            # Convert MongoDB ObjectId to string
            if "_id" in subscription_doc:
                subscription_doc["_id"] = str(subscription_doc["_id"])
            return Subscription(**subscription_doc)

        # Create default free subscription if none exists
        return await SubscriptionService.create_free_subscription(user_id)

    @staticmethod
    async def create_free_subscription(user_id: str) -> Subscription:
        """Create a default free subscription for new users"""
        db = await get_database()

        subscription = Subscription(
            user_id=user_id,
            tier=SubscriptionTier.FREE,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=365)  # So free tier doesn't expire
        )

        await db.subscriptions.insert_one(subscription.dict())
        logger.info(f"Created free subscription for user {user_id}")

        return subscription

    @staticmethod
    async def upgrade_to_premium(
        user_id: str,
        billing_period: BillingPeriod,
        stripe_subscription_id: str,
        stripe_customer_id: str,
        trial_days: Optional[int] = None
    ) -> Subscription:
        """Upgrade user to premium subscription"""
        db = await get_database()

        # Calculate period dates
        start_date = datetime.utcnow()
        if billing_period == BillingPeriod.MONTHLY:
            end_date = start_date + timedelta(days=30)
        else:  # YEARLY
            end_date = start_date + timedelta(days=365)

        # Handle trial period
        trial_end = None
        status = SubscriptionStatus.ACTIVE
        if trial_days:
            trial_end = start_date + timedelta(days=trial_days)
            status = SubscriptionStatus.TRIAL

        subscription = Subscription(
            user_id=user_id,
            tier=SubscriptionTier.PREMIUM,
            status=status,
            billing_period=billing_period,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id,
            current_period_start=start_date,
            current_period_end=end_date,
            trial_end=trial_end
        )

        # Deactivate previous subscriptions
        await db.subscriptions.update_many(
            {"user_id": user_id, "status": SubscriptionStatus.ACTIVE},
            {"$set": {"status": SubscriptionStatus.INACTIVE, "updated_at": datetime.utcnow()}}
        )

        # Insert new subscription
        await db.subscriptions.insert_one(subscription.dict())

        # Update user tier in users collection for backward compatibility
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"subscription_tier": "premium", "upgraded_at": datetime.utcnow()}}
        )

        logger.info(f"Upgraded user {user_id} to premium subscription")
        return subscription

    @staticmethod
    async def cancel_subscription(user_id: str, immediate: bool = False) -> bool:
        """Cancel user subscription"""
        db = await get_database()

        subscription = await SubscriptionService.get_user_subscription(user_id)
        if not subscription:
            return False

        update_data = {
            "cancelled_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        if immediate:
            update_data["status"] = SubscriptionStatus.CANCELLED
            update_data["current_period_end"] = datetime.utcnow()
        else:
            # Let it expire at the end of current period
            update_data["status"] = SubscriptionStatus.CANCELLED

        await db.subscriptions.update_one(
            {"user_id": user_id, "id": subscription.id},
            {"$set": update_data}
        )

        logger.info(f"Cancelled subscription for user {user_id}")
        return True

    @staticmethod
    async def check_usage_limits(user_id: str, feature: str) -> Dict[str, Any]:
        """Check if user can use a specific feature based on their subscription"""
        subscription = await SubscriptionService.get_user_subscription(user_id)
        limits = TIER_LIMITS[subscription.tier]

        result = {
            "allowed": True,
            "reason": None,
            "tier": subscription.tier,
            "usage_info": {}
        }

        if feature == "simulation":
            if limits.simulations_per_week is not None:
                # Check current week usage
                usage = await SubscriptionService.get_current_usage(user_id)
                if usage.simulations_used >= limits.simulations_per_week:
                    result["allowed"] = False
                    result["reason"] = f"Weekly limit of {limits.simulations_per_week} simulations reached"

                result["usage_info"] = {
                    "used": usage.simulations_used,
                    "limit": limits.simulations_per_week,
                    "remaining": limits.simulations_per_week - usage.simulations_used
                }

        elif feature == "risk_assessment":
            if limits.risk_assessments_per_week is not None:
                # Check current week usage
                usage = await SubscriptionService.get_current_usage(user_id)
                if usage.risk_assessments_used >= limits.risk_assessments_per_week:
                    result["allowed"] = False
                    result["reason"] = f"Weekly limit of {limits.risk_assessments_per_week} risk assessments reached"

                result["usage_info"] = {
                    "used": usage.risk_assessments_used,
                    "limit": limits.risk_assessments_per_week,
                    "remaining": limits.risk_assessments_per_week - usage.risk_assessments_used
                }

        elif feature == "advanced_simulation":
            if not limits.advanced_simulations:
                result["allowed"] = False
                result["reason"] = "Advanced simulations require premium subscription"

        elif feature == "ai_chatbot":
            if not limits.ai_chatbot_access:
                result["allowed"] = False
                result["reason"] = "AI chatbot requires premium subscription"

        elif feature == "custom_scenarios":
            if not limits.custom_scenarios:
                result["allowed"] = False
                result["reason"] = "Custom scenarios require premium subscription"

        return result

    @staticmethod
    async def get_current_usage(user_id: str) -> UsageTracking:
        """Get current period usage for user"""
        db = await get_database()
        subscription = await SubscriptionService.get_user_subscription(user_id)

        # Calculate current week period (Monday to Sunday)
        now = datetime.utcnow()
        days_since_monday = now.weekday()  # Monday is 0, Sunday is 6
        period_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=7)

        usage_doc = await db.usage_tracking.find_one({
            "user_id": user_id,
            "subscription_id": subscription.id,
            "period_start": {"$lte": now},
            "period_end": {"$gt": now}
        })

        if usage_doc:
            if "_id" in usage_doc:
                usage_doc["_id"] = str(usage_doc["_id"])
            return UsageTracking(**usage_doc)

        # Create new usage tracking record
        usage = UsageTracking(
            user_id=user_id,
            subscription_id=subscription.id,
            period_start=period_start,
            period_end=period_end
        )

        await db.usage_tracking.insert_one(usage.dict())
        return usage

    @staticmethod
    async def record_usage(user_id: str, feature: str, amount: int = 1) -> bool:
        """Record feature usage for billing and limits"""
        db = await get_database()
        usage = await SubscriptionService.get_current_usage(user_id)

        update_data = {"updated_at": datetime.utcnow()}

        if feature == "simulation":
            update_data["simulations_used"] = usage.simulations_used + amount
        elif feature == "risk_assessment":
            update_data["risk_assessments_used"] = usage.risk_assessments_used + amount
        else:
            # Update features_used dictionary
            features_used = usage.features_used.copy()
            features_used[feature] = features_used.get(feature, 0) + amount
            update_data["features_used"] = features_used

        await db.usage_tracking.update_one(
            {"user_id": user_id, "id": usage.id},
            {"$set": update_data}
        )

        return True

    @staticmethod
    async def get_subscription_analytics(user_id: str) -> Dict[str, Any]:
        """Get subscription and usage analytics for user"""
        subscription = await SubscriptionService.get_user_subscription(user_id)
        usage = await SubscriptionService.get_current_usage(user_id)
        limits = TIER_LIMITS[subscription.tier]

        return {
            "subscription": {
                "tier": subscription.tier,
                "status": subscription.status,
                "is_active": subscription.is_active(),
                "is_trial": subscription.is_trial(),
                "days_until_expiry": subscription.days_until_expiry(),
                "billing_period": subscription.billing_period
            },
            "usage": {
                "simulations_used": usage.simulations_used,
                "simulations_limit": limits.simulations_per_week,
                "risk_assessments_used": usage.risk_assessments_used,
                "risk_assessments_limit": limits.risk_assessments_per_week,
                "features_used": usage.features_used,
                "period_start": usage.period_start,
                "period_end": usage.period_end
            },
            "features": {
                "advanced_simulations": limits.advanced_simulations,
                "ai_chatbot_access": limits.ai_chatbot_access,
                "export_formats": limits.export_formats,
                "priority_support": limits.priority_support,
                "custom_scenarios": limits.custom_scenarios,
                "historical_data_months": limits.historical_data_months
            }
        }