"""
ML Prediction Service

Generates realistic predictions for life simulations using feature engineering
and statistical models. Can be extended with trained ML models.
"""

import logging
import random
from typing import List, Dict, Any
from datetime import datetime

from models.ml_models import (
    MLPredictionInput, MLPredictionResult, YearlyPrediction,
    CareerMetrics, LifeQualityMetrics, CareerField, EducationLevel
)
from ml.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)

class MLPredictionService:
    """Service for generating ML-based predictions"""

    MODEL_VERSION = "1.0.0-baseline"

    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        # In future, load trained models here
        # self.salary_model = joblib.load('models/salary_model.pkl')
        # self.satisfaction_model = joblib.load('models/satisfaction_model.pkl')

    def predict_timeline(
        self,
        input_data: MLPredictionInput,
        years: int = 10,
        start_year: int = None
    ) -> MLPredictionResult:
        """
        Generate predictions for a multi-year timeline

        Args:
            input_data: User and choice context
            years: Number of years to predict (default 10)
            start_year: Starting year (default: current year)

        Returns:
            MLPredictionResult with yearly predictions
        """
        if start_year is None:
            start_year = datetime.now().year

        predictions = []
        current_state = self._initialize_state(input_data)

        for year_offset in range(years):
            year = start_year + year_offset
            yearly_pred = self._predict_year(input_data, current_state, year, year_offset)
            predictions.append(yearly_pred)

            # Update state for next year
            current_state = self._update_state(current_state, yearly_pred, input_data)

        # Calculate overall confidence based on data quality
        confidence = self._calculate_confidence(input_data)

        return MLPredictionResult(
            predictions=predictions,
            confidence_score=confidence,
            model_version=self.MODEL_VERSION,
            prediction_metadata={
                "input_features": self.feature_engineer.encode_categorical_features(input_data),
                "start_year": start_year,
                "years_predicted": years
            }
        )

    def _initialize_state(self, input_data: MLPredictionInput) -> Dict[str, Any]:
        """Initialize the state for year 0"""
        base_salary = self.feature_engineer.calculate_base_salary(input_data)
        work_life_balance = self.feature_engineer.calculate_work_life_balance(input_data)

        return {
            "current_salary": base_salary,
            "position_level": input_data.position_level,
            "years_in_position": 0,
            "total_experience": input_data.years_experience,
            "work_life_balance": work_life_balance,
            "location": input_data.location_type.value,
            "promotions_received": 0,
            "performance_score": 7.0,  # Start with average performance
            "career_stability": self.feature_engineer.calculate_career_stability(input_data)
        }

    def _predict_year(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        year: int,
        year_offset: int
    ) -> YearlyPrediction:
        """Predict metrics for a single year"""

        # Career metrics
        career_metrics = self._predict_career_metrics(input_data, state, year_offset)

        # Life quality metrics
        life_quality = self._predict_life_quality(input_data, state, career_metrics, year_offset)

        # Major life events
        events = self._predict_major_events(input_data, state, year_offset)

        return YearlyPrediction(
            year=year,
            career_metrics=career_metrics,
            life_quality=life_quality,
            major_event_probability=events,
            location=state["location"]
        )

    def _predict_career_metrics(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        year_offset: int
    ) -> CareerMetrics:
        """Predict career-related metrics"""

        # Salary growth
        salary = self._predict_salary_growth(input_data, state, year_offset)

        # Promotion probability
        promotion_prob = self.feature_engineer.calculate_promotion_probability(
            input_data,
            state["years_in_position"],
            state["performance_score"]
        )

        # Position title
        position_title = self._generate_position_title(
            input_data.career_field,
            state["position_level"],
            state["total_experience"] + year_offset
        )

        # Career stability (adjusts over time)
        stability = state["career_stability"]
        if year_offset > 2:  # Stability improves after initial transition
            stability = min(10.0, stability + 0.3 * year_offset)

        # Job satisfaction
        satisfaction = self.feature_engineer.calculate_job_satisfaction(
            input_data,
            state["work_life_balance"]
        )
        # Adjust for time (novelty wears off or improves)
        if input_data.is_career_change and year_offset < 3:
            satisfaction -= (3 - year_offset) * 0.3  # Gradual adaptation
        elif year_offset > 5:
            satisfaction += min(1.0, (year_offset - 5) * 0.1)  # Mastery satisfaction

        # Work-life balance (can change with promotions)
        work_life_balance = state["work_life_balance"]

        # Stress level
        stress = self.feature_engineer.calculate_stress_level(input_data, work_life_balance)

        return CareerMetrics(
            salary=round(salary, 2),
            promotion_probability=round(promotion_prob, 3),
            position_title=position_title,
            career_stability=round(stability, 1),
            job_satisfaction=round(max(1.0, min(10.0, satisfaction)), 1),
            work_life_balance=round(work_life_balance, 1),
            stress_level=round(stress, 1)
        )

    def _predict_life_quality(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        career_metrics: CareerMetrics,
        year_offset: int
    ) -> LifeQualityMetrics:
        """Predict life quality metrics"""

        current_age = input_data.age + year_offset

        # Financial security
        financial_security = self.feature_engineer.calculate_financial_security(
            career_metrics.salary,
            current_age,
            input_data.location_type
        )

        # Health score
        health = self.feature_engineer.calculate_health_score(
            current_age,
            career_metrics.stress_level,
            career_metrics.work_life_balance,
            financial_security
        )

        # Relationship quality (influenced by work-life balance and stability)
        relationship = self._predict_relationship_quality(
            career_metrics.work_life_balance,
            career_metrics.stress_level,
            state["career_stability"],
            year_offset
        )

        # Personal growth (influenced by job satisfaction and new experiences)
        personal_growth = self._predict_personal_growth(
            career_metrics.job_satisfaction,
            input_data.is_career_change,
            year_offset
        )

        # Overall happiness (weighted combination)
        happiness = (
            career_metrics.job_satisfaction * 0.25 +
            financial_security * 0.20 +
            health * 0.20 +
            relationship * 0.20 +
            personal_growth * 0.15
        )

        return LifeQualityMetrics(
            happiness_score=round(max(1.0, min(10.0, happiness)), 1),
            financial_security=round(financial_security, 1),
            health_score=round(health, 1),
            relationship_quality=round(relationship, 1),
            personal_growth=round(personal_growth, 1)
        )

    def _predict_salary_growth(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        year_offset: int
    ) -> float:
        """Predict salary with realistic growth patterns"""

        current_salary = state["current_salary"]

        # Base annual growth (inflation + merit)
        base_growth_rate = 0.03 + input_data.industry_growth_rate

        # Performance-based growth
        performance_factor = state["performance_score"] / 7.0
        growth_rate = base_growth_rate * performance_factor

        # Apply growth
        new_salary = current_salary * (1 + growth_rate)

        # Add random variation (±5%)
        variation = random.uniform(-0.05, 0.05)
        new_salary *= (1 + variation)

        return new_salary

    def _predict_relationship_quality(
        self,
        work_life_balance: float,
        stress_level: float,
        career_stability: float,
        year_offset: int
    ) -> float:
        """Predict relationship quality score"""

        # Work-life balance is primary factor
        base_quality = work_life_balance * 0.6

        # Low stress helps relationships
        base_quality += (10 - stress_level) * 0.3

        # Career stability provides security
        base_quality += career_stability * 0.1

        # Relationships generally improve over time (up to a point)
        time_factor = min(1.5, 1 + year_offset * 0.05)
        quality = base_quality * time_factor

        # Add some randomness for life events
        quality += random.uniform(-0.5, 0.5)

        return max(1.0, min(10.0, quality))

    def _predict_personal_growth(
        self,
        job_satisfaction: float,
        is_career_change: bool,
        year_offset: int
    ) -> float:
        """Predict personal growth score"""

        # Career changes provide high growth initially
        if is_career_change and year_offset < 3:
            base_growth = 8.5 - year_offset * 0.5
        else:
            base_growth = 7.0

        # Job satisfaction correlates with growth opportunities
        growth = base_growth * 0.5 + job_satisfaction * 0.5

        # Growth tends to plateau over time in same role
        if year_offset > 5 and not is_career_change:
            growth -= (year_offset - 5) * 0.2

        # Add variation
        growth += random.uniform(-0.3, 0.3)

        return max(1.0, min(10.0, growth))

    def _predict_major_events(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        year_offset: int
    ) -> Dict[str, float]:
        """Predict probability of major life events"""

        events = {}

        # Promotion (already calculated in career metrics)
        promotion_prob = self.feature_engineer.calculate_promotion_probability(
            input_data,
            state["years_in_position"],
            state["performance_score"]
        )
        if promotion_prob > 0.1:
            events["promotion"] = promotion_prob

        # Job change (higher if low satisfaction)
        if state.get("job_satisfaction", 7) < 5:
            events["job_change"] = 0.15 + (5 - state.get("job_satisfaction", 7)) * 0.05

        # Relocation (lower after initial move)
        if input_data.is_location_change and year_offset < 2:
            events["relocation"] = 0.05
        elif year_offset > 5:
            events["relocation"] = 0.08

        # Major purchase (based on financial security)
        financial_security = state.get("financial_security", 5)
        if financial_security > 7:
            events["major_purchase"] = 0.12

        # Career milestone (based on experience)
        total_exp = state["total_experience"] + year_offset
        if total_exp % 5 == 0 and total_exp > 0:  # Every 5 years
            events["career_milestone"] = 0.6

        return events

    def _update_state(
        self,
        state: Dict[str, Any],
        prediction: YearlyPrediction,
        input_data: MLPredictionInput
    ) -> Dict[str, Any]:
        """Update state based on current year's prediction"""

        new_state = state.copy()

        # Update salary
        new_state["current_salary"] = prediction.career_metrics.salary

        # Check for promotion
        if random.random() < prediction.career_metrics.promotion_probability:
            new_state = self._apply_promotion(new_state, input_data)
        else:
            new_state["years_in_position"] += 1

        # Update experience
        new_state["total_experience"] += 1

        # Update performance (random walk around 7.0)
        performance_change = random.uniform(-0.5, 0.5)
        new_state["performance_score"] = max(4.0, min(10.0,
            new_state["performance_score"] + performance_change
        ))

        # Update work-life balance
        new_state["work_life_balance"] = prediction.career_metrics.work_life_balance

        # Update career stability
        new_state["career_stability"] = prediction.career_metrics.career_stability

        return new_state

    def _apply_promotion(
        self,
        state: Dict[str, Any],
        input_data: MLPredictionInput
    ) -> Dict[str, Any]:
        """Apply promotion effects to state"""

        position_progression = ["entry", "mid", "senior", "lead", "executive"]
        current_idx = position_progression.index(state["position_level"])

        if current_idx < len(position_progression) - 1:
            new_state = state.copy()
            new_state["position_level"] = position_progression[current_idx + 1]
            new_state["years_in_position"] = 0
            new_state["promotions_received"] += 1

            # Promotion typically comes with salary bump
            new_state["current_salary"] *= random.uniform(1.10, 1.25)

            # Work-life balance may decrease with higher responsibility
            new_state["work_life_balance"] = max(3.0, new_state["work_life_balance"] - 0.5)

            return new_state

        return state

    def _generate_position_title(
        self,
        career_field: CareerField,
        position_level: str,
        years_experience: float
    ) -> str:
        """Generate realistic position title"""

        titles = {
            CareerField.TECHNOLOGY: {
                "entry": "Software Engineer I",
                "mid": "Software Engineer II",
                "senior": "Senior Software Engineer",
                "lead": "Engineering Manager",
                "executive": "VP of Engineering"
            },
            CareerField.FINANCE: {
                "entry": "Financial Analyst",
                "mid": "Senior Financial Analyst",
                "senior": "Finance Manager",
                "lead": "Director of Finance",
                "executive": "Chief Financial Officer"
            },
            CareerField.HEALTHCARE: {
                "entry": "Healthcare Professional",
                "mid": "Senior Healthcare Professional",
                "senior": "Department Head",
                "lead": "Medical Director",
                "executive": "Chief Medical Officer"
            },
            CareerField.ENGINEERING: {
                "entry": "Engineer I",
                "mid": "Engineer II",
                "senior": "Senior Engineer",
                "lead": "Principal Engineer",
                "executive": "VP of Engineering"
            },
            CareerField.EDUCATION: {
                "entry": "Teacher",
                "mid": "Senior Teacher",
                "senior": "Department Chair",
                "lead": "Assistant Principal",
                "executive": "Principal"
            },
            CareerField.BUSINESS: {
                "entry": "Business Analyst",
                "mid": "Senior Business Analyst",
                "senior": "Business Manager",
                "lead": "Director",
                "executive": "VP of Operations"
            },
            CareerField.CREATIVE: {
                "entry": "Junior Designer",
                "mid": "Designer",
                "senior": "Senior Designer",
                "lead": "Design Lead",
                "executive": "Creative Director"
            },
            CareerField.SERVICE: {
                "entry": "Service Representative",
                "mid": "Senior Service Representative",
                "senior": "Service Manager",
                "lead": "Regional Manager",
                "executive": "Director of Operations"
            },
            CareerField.OTHER: {
                "entry": "Associate",
                "mid": "Senior Associate",
                "senior": "Manager",
                "lead": "Senior Manager",
                "executive": "Director"
            }
        }

        return titles[career_field][position_level]

    def _calculate_confidence(self, input_data: MLPredictionInput) -> float:
        """Calculate prediction confidence based on data completeness"""

        confidence = 0.75  # Base confidence

        # Higher confidence if we have current salary
        if input_data.current_salary:
            confidence += 0.1

        # Higher confidence for more experience
        if input_data.years_experience > 3:
            confidence += 0.05

        # Lower confidence for career changes
        if input_data.is_career_change:
            confidence -= 0.1

        # Lower confidence for location changes
        if input_data.is_location_change:
            confidence -= 0.05

        return max(0.5, min(1.0, confidence))
