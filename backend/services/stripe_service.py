import os
import logging
import stripe
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe_api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe_checkout = StripeCheckout(api_key=stripe_api_key) if stripe_api_key else None

async def create_stripe_checkout(amount: float, currency: str, success_url: str, cancel_url: str, metadata: dict = None):
    """Create Stripe checkout session"""
    if not stripe_checkout:
        raise Exception("Stripe not configured")
    
    try:
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency=currency,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {}
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        return {
            "url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logger.error(f"Stripe checkout creation failed: {e}")
        raise Exception(f"Failed to create checkout session: {str(e)}")

async def get_stripe_payment_status(session_id: str):
    """Get payment status from Stripe"""
    if not stripe_checkout:
        raise Exception("Stripe not configured")
    
    try:
        status_response = await stripe_checkout.get_checkout_status(session_id)
        
        return {
            "payment_status": status_response.payment_status,
            "amount_total": status_response.amount_total,
            "currency": status_response.currency,
            "status": status_response.status,
            "metadata": status_response.metadata
        }
        
    except Exception as e:
        logger.error(f"Stripe status check failed: {e}")
        raise Exception(f"Failed to check payment status: {str(e)}")