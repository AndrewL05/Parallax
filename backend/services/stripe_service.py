import os
import logging
import stripe
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

async def create_stripe_checkout(amount: float, currency: str, success_url: str, cancel_url: str, metadata: dict = None):
    """Create Stripe checkout session"""
    if not stripe.api_key:
        raise Exception("Stripe not configured")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'Parallax Premium',
                    },
                    'unit_amount': int(amount * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {}
        )
        
        return {
            "url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        logger.error(f"Stripe checkout creation failed: {e}")
        raise Exception(f"Failed to create checkout session: {str(e)}")

async def get_stripe_payment_status(session_id: str):
    """Get payment status from Stripe"""
    if not stripe.api_key:
        raise Exception("Stripe not configured")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Map Stripe payment status to our expected values
        status_mapping = {
            "paid": "paid",
            "unpaid": "initiated",
            "no_payment_required": "paid",
        }
        
        logger.info(f"Stripe session payment_status: {session.payment_status}")
        payment_status = status_mapping.get(session.payment_status, "initiated")
        logger.info(f"Mapped payment_status: {payment_status}")
        
        return {
            "payment_status": payment_status,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "status": session.status,
            "metadata": session.metadata
        }
        
    except Exception as e:
        logger.error(f"Stripe status check failed: {e}")
        raise Exception(f"Failed to check payment status: {str(e)}")