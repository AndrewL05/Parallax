"""
Centralized Configuration for Parallax Backend

All configurable values should be defined here and imported by other modules.
Environment variables override defaults where applicable.
"""

import os
from typing import List

# =============================================================================
# API & Server Configuration
# =============================================================================

SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

API_VERSION = "1.0.0"
API_TITLE = "Parallax Life Simulator API"

# CORS Origins - extend via CORS_ORIGINS env var (comma-separated)
DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

def get_cors_origins() -> List[str]:
    """Get CORS origins from environment or use defaults."""
    env_origins = os.getenv("CORS_ORIGINS")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",")]
    return DEFAULT_CORS_ORIGINS

CORS_ORIGINS = get_cors_origins()

# =============================================================================
# OpenRouter / LLM Configuration
# =============================================================================

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Model selection
LLM_MODEL_PRIMARY = os.getenv("LLM_MODEL_PRIMARY", "openai/gpt-3.5-turbo")
LLM_MODEL_FAST = os.getenv("LLM_MODEL_FAST", "meta-llama/llama-3.2-3b-instruct:free")

# LLM Request Parameters
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS_SIMULATION = int(os.getenv("LLM_MAX_TOKENS_SIMULATION", "3000"))
LLM_MAX_TOKENS_NARRATIVE = int(os.getenv("LLM_MAX_TOKENS_NARRATIVE", "500"))
LLM_MAX_TOKENS_COMPARISON = int(os.getenv("LLM_MAX_TOKENS_COMPARISON", "400"))
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "45.0"))

# =============================================================================
# ML Model Paths
# =============================================================================

ML_MODELS_DIR = os.getenv("ML_MODELS_DIR", "ml/models")

# =============================================================================
# Salary & Career Constants
# =============================================================================

# Annual growth rates
ANNUAL_INFLATION_RATE = 0.03
ANNUAL_MERIT_GROWTH_RATE = 0.02
ANNUAL_TRAINING_RAISE_RATE = 0.03
POST_TRAINING_GROWTH_RATE = 0.05

# Experience multipliers
EXPERIENCE_MULTIPLIER_PER_YEAR = 0.02
EXPERIENCE_MULTIPLIER_CAP = 0.5
REMOTE_WORK_SALARY_BONUS = 0.10

# Salary validation
SALARY_VARIANCE_THRESHOLD = 1000  # Minimum difference to log correction
SALARY_NATURAL_VARIANCE = 0.05   # ±5% variance for natural-looking predictions

# Location cost-of-living multipliers
LOCATION_MULTIPLIERS = {
    "major_city": 1.3,
    "small_city": 1.1,
    "suburb": 1.0,
    "rural": 0.85,
    "international": 0.9,
}

# Industry growth rates
INDUSTRY_GROWTH_RATES = {
    "technology": 0.08,
    "healthcare": 0.06,
    "finance": 0.04,
    "engineering": 0.05,
    "education": 0.02,
    "business": 0.04,
    "creative": 0.03,
    "service": 0.03,
    "other": 0.03,
}

# =============================================================================
# Database Configuration
# =============================================================================

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "parallax")

# =============================================================================
# Feature Flags
# =============================================================================

ENABLE_ML_PREDICTIONS = os.getenv("ENABLE_ML_PREDICTIONS", "true").lower() == "true"
ENABLE_AI_NARRATIVES = os.getenv("ENABLE_AI_NARRATIVES", "true").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
