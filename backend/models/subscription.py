from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"

class BillingPeriod(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tier: SubscriptionTier = SubscriptionTier.FREE
    status: SubscriptionStatus = SubscriptionStatus.INACTIVE
    billing_period: Optional[BillingPeriod] = None
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False

        if self.current_period_end and self.current_period_end < datetime.utcnow():
            return False

        return True

    def is_trial(self) -> bool:
        """Check if user is in trial period"""
        return (
            self.status == SubscriptionStatus.TRIAL and
            self.trial_end and
            self.trial_end > datetime.utcnow()
        )

    def has_premium_access(self) -> bool:
        """Check if user has premium features access"""
        return (
            self.tier == SubscriptionTier.PREMIUM and
            (self.is_active() or self.is_trial())
        )

    def days_until_expiry(self) -> Optional[int]:
        """Get days until subscription expires"""
        if not self.current_period_end:
            return None

        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)

class UsageLimit(BaseModel):
    """Define usage limits for different subscription tiers"""
    tier: SubscriptionTier
    simulations_per_week: Optional[int] = None  # None = unlimited
    risk_assessments_per_week: Optional[int] = None  # None = unlimited
    advanced_simulations: bool = False
    ai_chatbot_access: bool = True  # Free for all users
    export_formats: list[str] = Field(default_factory=lambda: ["json", "pdf"])
    priority_support: bool = False
    custom_scenarios: bool = False
    historical_data_months: int = 1  # How far back user can view data

# Define tier limits
TIER_LIMITS = {
    SubscriptionTier.FREE: UsageLimit(
        tier=SubscriptionTier.FREE,
        simulations_per_week=3,
        risk_assessments_per_week=3,
        advanced_simulations=False,
        ai_chatbot_access=True,  # Free access to AI chatbot
        export_formats=["json", "pdf"],  # PDF included for free
        priority_support=False,
        custom_scenarios=False,
        historical_data_months=1
    ),
    SubscriptionTier.PREMIUM: UsageLimit(
        tier=SubscriptionTier.PREMIUM,
        simulations_per_week=None,  # Unlimited
        risk_assessments_per_week=None,  # Unlimited
        advanced_simulations=True,
        ai_chatbot_access=True,
        export_formats=["json", "pdf", "csv", "excel"],
        priority_support=True,
        custom_scenarios=True,
        historical_data_months=12
    )
}

class UsageTracking(BaseModel):
    """Track user usage for billing and limits"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subscription_id: str
    period_start: datetime
    period_end: datetime
    simulations_used: int = 0
    risk_assessments_used: int = 0
    features_used: Dict[str, int] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }