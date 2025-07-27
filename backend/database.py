from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def get_database():
    """Get database connection"""
    return db

async def init_database():
    """Initialize database with indexes"""
    try:
        # Create indexes for better performance
        
        # Users collection indexes
        await db.users.create_index("clerk_id", unique=True)
        await db.users.create_index("email")
        await db.users.create_index("created_at")
        
        # Simulations collection indexes
        await db.simulations.create_index("user_id")
        await db.simulations.create_index("created_at")
        await db.simulations.create_index("id", unique=True)
        await db.simulations.create_index([("user_id", 1), ("created_at", -1)])
        
        # Payment transactions collection indexes
        await db.payment_transactions.create_index("session_id", unique=True)
        await db.payment_transactions.create_index("user_id")
        await db.payment_transactions.create_index("created_at")
        await db.payment_transactions.create_index("payment_status")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

async def close_database():
    """Close database connection"""
    client.close()