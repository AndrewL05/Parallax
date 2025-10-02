from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
import logging
from datetime import datetime

from models.payment import PaymentTransaction, PaymentStatus, CheckoutRequest
from models.subscription import BillingPeriod
from database import get_database
from auth import get_current_user
from services.stripe_service import create_stripe_checkout, get_stripe_payment_status
from services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])

# Define packages (server-side only for security)
PACKAGES = {
    "premium_monthly": {"amount": 4.99, "name": "Premium Monthly"}
}

@router.post("/checkout")
async def create_checkout_session(
    request: Request,
    package: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Create Stripe checkout session for premium subscription"""
    if package not in PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    package_info = PACKAGES[package]
    db = await get_database()
    
    try:
        # Get origin from request headers or use default
        origin_url = str(request.base_url).rstrip('/')
        if origin_url.endswith('/api'):
            origin_url = origin_url[:-4]
        
        # Create checkout session
        session_data = await create_stripe_checkout(
            amount=package_info["amount"],
            currency="usd",
            success_url=f"{origin_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{origin_url}",
            metadata={
                "package": package,
                "user_id": str(current_user.get("clerk_id")) if current_user else "anonymous"
            }
        )

        # Save transaction record
        transaction = PaymentTransaction(
            user_id=str(current_user.get("clerk_id")) if current_user else None,
            session_id=session_data["session_id"],
            amount=package_info["amount"],
            payment_status="initiated",
            package_type=package,
            metadata={"package": package}
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        logger.info(f"Checkout session created: {session_data['session_id']}")
        return {"checkout_url": session_data["url"], "session_id": session_data["session_id"]}
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@router.get("/status/{session_id}")
async def get_payment_status(session_id: str):
    """Check payment status and update user subscription"""
    db = await get_database()
    
    try:
        # Get status from Stripe
        status_response = await get_stripe_payment_status(session_id)
        
        # Update transaction record
        update_data = {
            "payment_status": status_response["payment_status"],
            "updated_at": datetime.utcnow()
        }
        
        if status_response["payment_status"] == "paid":
            update_data["completed_at"] = datetime.utcnow()
        
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        # If payment successful, upgrade user subscription
        if status_response["payment_status"] == "paid":
            transaction = await db.payment_transactions.find_one({"session_id": session_id})
            if transaction and transaction.get("user_id"):
                # Determine billing period from package
                billing_period = BillingPeriod.YEARLY if "yearly" in transaction.get("package_type", "") else BillingPeriod.MONTHLY

                # Create premium subscription using new service
                await SubscriptionService.upgrade_to_premium(
                    user_id=transaction["user_id"],
                    billing_period=billing_period,
                    stripe_subscription_id=session_id,  # In production, use actual Stripe subscription ID
                    stripe_customer_id=status_response.get("customer", ""),
                    trial_days=None  # No trial for direct payments
                )

                # Update legacy user record for backward compatibility
                await db.users.update_one(
                    {"_id": transaction["user_id"]},
                    {"$set": {"subscription_tier": "premium", "upgraded_at": datetime.utcnow()}}
                )
                logger.info(f"User {transaction['user_id']} upgraded to premium")
        
        return {
            "payment_status": status_response["payment_status"],
            "amount": status_response["amount_total"] / 100,  # Convert from cents
            "currency": status_response["currency"],
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Payment status check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@router.get("/transactions")
async def get_user_transactions(current_user: dict = Depends(get_current_user)):
    """Get payment transactions for the authenticated user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db = await get_database()
    user_doc = await db.users.find_one({"clerk_id": current_user["clerk_id"]})
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = await db.payment_transactions.find(
        {"user_id": str(user_doc["_id"])}
    ).sort("created_at", -1).to_list(50)
    
    # Convert ObjectId to string
    for transaction in transactions:
        if "_id" in transaction:
            transaction["_id"] = str(transaction["_id"])
    
    return transactions

@router.post("/subscription/cancel")
async def cancel_subscription(
    immediate: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Cancel user's premium subscription"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("clerk_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user data")

    success = await SubscriptionService.cancel_subscription(user_id, immediate)

    if not success:
        raise HTTPException(status_code=404, detail="No active subscription found")

    return {
        "message": "Subscription cancelled successfully",
        "immediate": immediate,
        "cancelled_at": datetime.utcnow()
    }

@router.get("/subscription/status")
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """Get detailed subscription status"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("clerk_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user data")

    analytics = await SubscriptionService.get_subscription_analytics(user_id)

    return analytics

@router.post("/subscription/trial")
async def start_trial(
    trial_days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Start a premium trial for eligible users"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("clerk_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user data")

    subscription = await SubscriptionService.get_user_subscription(user_id)

    # Check if user is eligible for trial
    if subscription.tier != "free":
        raise HTTPException(
            status_code=400,
            detail="Trial only available for free tier users"
        )

    # Check if user has already had a trial
    db = await get_database()
    existing_trial = await db.subscriptions.find_one({
        "user_id": user_id,
        "trial_end": {"$exists": True}
    })

    if existing_trial:
        raise HTTPException(
            status_code=400,
            detail="Trial already used for this account"
        )

    # Create trial subscription
    trial_subscription = await SubscriptionService.upgrade_to_premium(
        user_id=user_id,
        billing_period=BillingPeriod.MONTHLY,
        stripe_subscription_id=f"trial_{datetime.utcnow().timestamp()}",
        stripe_customer_id="",
        trial_days=trial_days
    )

    return {
        "message": "Trial started successfully",
        "trial_days": trial_days,
        "trial_end": trial_subscription.trial_end,
        "subscription_id": trial_subscription.id
    }