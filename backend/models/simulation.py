from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid

class LifeChoice(BaseModel):
    model_config = {"extra": "ignore"}  # Ignore extra fields
    
    title: str
    description: str
    category: str  # career, location, education, relationship, etc.

class UserContext(BaseModel):
    model_config = {"extra": "ignore"}  # Ignore extra fields
    
    age: Optional[Union[str, int]] = None
    current_location: Optional[str] = None
    current_salary: Optional[Union[str, int, float]] = None
    education_level: Optional[str] = None
    
    @field_validator('age', mode='before')
    @classmethod
    def convert_age_to_string(cls, v):
        if v is not None:
            return str(v)
        return v
    
    @field_validator('current_salary', mode='before')
    @classmethod
    def convert_salary_to_string(cls, v):
        if v is not None:
            return str(v)
        return v

class SimulationRequest(BaseModel):
    model_config = {"extra": "ignore"}  # Ignore extra fields
    
    choice_a: LifeChoice
    choice_b: LifeChoice
    user_context: Optional[UserContext] = None
    
    @field_validator('user_context', mode='before')
    @classmethod
    def validate_user_context(cls, v):
        if v is None or v == {}:
            return UserContext()
        return v

class TimelinePoint(BaseModel):
    year: int
    salary: Optional[float] = None
    happiness_score: float  # 1-10 scale
    major_event: Optional[str] = None
    location: Optional[str] = None
    career_title: Optional[str] = None

class Simulation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    choice_a: LifeChoice
    choice_b: LifeChoice
    user_context: Optional[UserContext] = None
    choice_a_timeline: List[TimelinePoint]
    choice_b_timeline: List[TimelinePoint]
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SimulationResult(BaseModel):
    id: str
    choice_a_timeline: List[TimelinePoint]
    choice_b_timeline: List[TimelinePoint]
    summary: str
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }