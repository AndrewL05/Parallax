from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid

class LifeChoice(BaseModel):
    title: str
    description: str
    category: str  

class UserContext(BaseModel):
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
    choice_a: LifeChoice
    choice_b: LifeChoice
    user_context: Optional[UserContext] = UserContext()

class TimelinePoint(BaseModel):
    year: int
    salary: Optional[float] = None
    happiness_score: float  
    major_event: Optional[str] = None
    location: Optional[str] = None
    career_title: Optional[str] = None

class Simulation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    choice_a: LifeChoice
    choice_b: LifeChoice
    user_context: UserContext
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