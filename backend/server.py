from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from config import CORS_ORIGINS, API_TITLE, API_VERSION, SERVER_HOST, SERVER_PORT
from routes.auth import router as auth_router
from routes.simulation import router as simulation_router
from routes.payments import router as payments_router
from routes.premium import router as premium_router
from routes.ml_scenarios import router as ml_scenarios_router
from database import init_database, close_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=API_TITLE, version=API_VERSION)

logger.info(f"CORS origins configured: {CORS_ORIGINS}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response

    if request.url.path == "/api/simulate":
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request path: {request.url.path}")
        logger.info(f"Content-Type: {request.headers.get('content-type')}")
        logger.info(f"Authorization header present: {bool(request.headers.get('authorization'))}")

    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Request validation failed"
        }
    )

app.include_router(auth_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(premium_router, prefix="/api")
app.include_router(ml_scenarios_router)

@app.get("/api/")
async def root():
    """API health check"""
    return {"message": API_TITLE, "version": API_VERSION, "status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Parallax Life Simulator API...")
    try:
        await init_database()
        logger.info("Database initialized successfully")

        from routes.ml_scenarios import get_scenario_service
        service = get_scenario_service()
        logger.info("ML scenario service initialized successfully")
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
        "service": API_TITLE,
        "version": API_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)