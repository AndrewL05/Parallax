from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routes
from routes.auth import router as auth_router
from routes.simulation import router as simulation_router
from routes.payments import router as payments_router
from routes.premium import router as premium_router
from database import init_database, close_database

# Initialize FastAPI app
app = FastAPI(title="Parallax Life Simulator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug middleware to log requests 
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path == "/api/simulate":
        logger.info(f"🔍 Request method: {request.method}")
        logger.info(f"🔍 Request path: {request.url.path}")
        logger.info(f"🔍 Content-Type: {request.headers.get('content-type')}")
        logger.info(f"🔍 Authorization header: {bool(request.headers.get('authorization'))}")
    
    response = await call_next(request)
    return response

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error on {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Request validation failed"
        }
    )

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(premium_router, prefix="/api")

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
    uvicorn.run(app, host="0.0.0.0", port=8000)