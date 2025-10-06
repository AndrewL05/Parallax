from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def get_database():
    """Get database connection"""
    return db

async def init_database():
    """Initialize database with indexes"""
    try:
        
        # Indexes
        # Users collection indexes
        await db.users.create_index("clerk_id", unique=True)
        await db.users.create_index("email")
        await db.users.create_index("created_at")
        
        # Simulations
        await db.simulations.create_index("user_id")
        await db.simulations.create_index("created_at")
        await db.simulations.create_index("id", unique=True)
        await db.simulations.create_index([("user_id", 1), ("created_at", -1)])
        
        # Payment transactions
        await db.payment_transactions.create_index("session_id", unique=True)
        await db.payment_transactions.create_index("user_id")
        await db.payment_transactions.create_index("created_at")
        await db.payment_transactions.create_index("payment_status")

        # Subscriptions
        await db.subscriptions.create_index("user_id")
        await db.subscriptions.create_index("id", unique=True)
        await db.subscriptions.create_index("stripe_subscription_id")
        await db.subscriptions.create_index("status")
        await db.subscriptions.create_index([("user_id", 1), ("created_at", -1)])
        await db.subscriptions.create_index("current_period_end")

        # Usage tracking
        await db.usage_tracking.create_index("user_id")
        await db.usage_tracking.create_index("subscription_id")
        await db.usage_tracking.create_index("id", unique=True)
        await db.usage_tracking.create_index([("user_id", 1), ("period_start", 1), ("period_end", 1)])

        # Custom scenarios
        await db.custom_scenarios.create_index("user_id")
        await db.custom_scenarios.create_index("id", unique=True)
        await db.custom_scenarios.create_index("is_public")
        await db.custom_scenarios.create_index("created_at")

        # Feedback
        await db.feedback.create_index("user_id")
        await db.feedback.create_index("id", unique=True)
        await db.feedback.create_index("type")
        await db.feedback.create_index("priority")
        await db.feedback.create_index("created_at")

        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

async def close_database():
    """Close database connection"""
    client.close()