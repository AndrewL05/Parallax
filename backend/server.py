from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routes
from .routes.auth import router as auth_router
from .routes.simulation import router as simulation_router  
from .routes.payments import router as payments_router
from .database import init_database, close_database

# Initialize FastAPI app
app = FastAPI(title="Parallax Life Simulator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(payments_router, prefix="/api")

@app.get("/api/")
async def root():
    """API health check"""
    return {"message": "Parallax Life Simulator API", "version": "1.0.0", "status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Parallax Life Simulator API...")
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Parallax Life Simulator API...")
    try:
        await close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "service": "Parallax Life Simulator API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)