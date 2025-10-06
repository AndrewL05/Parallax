from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class CareerField(str, Enum):
    """Career field categories"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    ENGINEERING = "engineering"
    BUSINESS = "business"
    CREATIVE = "creative"
    SERVICE = "service"
    OTHER = "other"

class EducationLevel(str, Enum):
    """Education levels"""
    HIGH_SCHOOL = "high_school"
    ASSOCIATES = "associates"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"
    BOOTCAMP = "bootcamp"
    SELF_TAUGHT = "self_taught"

class LocationType(str, Enum):
    """Location types for cost of living"""
    MAJOR_CITY = "major_city"
    SUBURB = "suburb"
    SMALL_CITY = "small_city"
    RURAL = "rural"
    INTERNATIONAL = "international"

class MLPredictionInput(BaseModel):
    """Input features for ML predictions"""
    # User context
    age: int = Field(..., ge=18, le=100)
    education_level: EducationLevel
    years_experience: float = Field(0, ge=0, le=50)
    current_salary: Optional[float] = Field(None, ge=0)

    # Career context
    career_field: CareerField
    position_level: str  
    location_type: LocationType

    # Choice-specific
    is_career_change: bool = False
    is_location_change: bool = False
    industry_growth_rate: float = Field(0.03, ge=-0.2, le=0.5)  

    # Optional factors
    has_remote_option: bool = False
    company_size: Optional[str] = None  

    class Config:
        use_enum_values = True

class CareerMetrics(BaseModel):
    """Career-related predictions"""
    salary: float = Field(..., ge=0)
    promotion_probability: float = Field(..., ge=0, le=1)
    position_title: str
    career_stability: float = Field(..., ge=0, le=10)  
    job_satisfaction: float = Field(..., ge=0, le=10)  
    work_life_balance: float = Field(..., ge=0, le=10)  
    stress_level: float = Field(..., ge=0, le=10)  

class LifeQualityMetrics(BaseModel):
    """Life quality predictions"""
    happiness_score: float = Field(..., ge=0, le=10)  
    financial_security: float = Field(..., ge=0, le=10)  
    health_score: float = Field(..., ge=0, le=10)  
    relationship_quality: float = Field(..., ge=0, le=10)  
    personal_growth: float = Field(..., ge=0, le=10)  

class YearlyPrediction(BaseModel):
    """Predictions for a single year"""
    year: int
    career_metrics: CareerMetrics
    life_quality: LifeQualityMetrics
    major_event_probability: Dict[str, float] = Field(default_factory=dict)
    location: str

class MLPredictionResult(BaseModel):
    """Complete ML prediction result for a 10-year timeline"""
    predictions: List[YearlyPrediction]
    confidence_score: float = Field(..., ge=0, le=1)
    model_version: str
    prediction_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DatasetMetadata(BaseModel):
    """Metadata for ML training datasets"""
    dataset_name: str
    source: str  
    version: str
    download_url: Optional[str] = None
    local_path: Optional[str] = None
    num_records: Optional[int] = None
    features: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ModelMetrics(BaseModel):
    """ML model performance metrics"""
    model_name: str
    model_type: str  
    accuracy: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    training_samples: int
    validation_samples: int
    training_date: datetime = Field(default_factory=datetime.utcnow)
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
