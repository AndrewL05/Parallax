from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: str
    amount: float
    currency: str = "usd"
    payment_status: str  # initiated, paid, failed, expired
    package_type: Optional[str] = None  # premium_monthly, premium_yearly
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaymentStatus(BaseModel):
    payment_status: str
    amount: float
    currency: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = {}

class CheckoutRequest(BaseModel):
    package: str  # premium_monthly, premium_yearly
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}