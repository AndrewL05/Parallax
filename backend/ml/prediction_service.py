"""
ML Prediction Service

Generates predictions for life simulations using a trained XGBoost model
for salary and feature engineering for life-quality metrics.
"""

import logging
import random
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.ml_models import (
    MLPredictionInput, MLPredictionResult, YearlyPrediction,
    CareerMetrics, LifeQualityMetrics, CareerField, EducationLevel
)
from ml.feature_engineering import FeatureEngineer
from ml.profession_data import (
    get_training_config,
    get_training_career_title,
    get_profession_titles_by_level,
    PROFESSION_SALARIES,
    TRAINING_CAREERS,
    PROFESSION_TO_FIELD,
)

logger = logging.getLogger(__name__)

POSITION_LEVELS = ["entry", "mid", "senior", "lead", "executive"]


class MLPredictionService:
    """Service for generating ML-based predictions using trained models."""

    MODEL_VERSION = "2.0.0-xgboost"

    def __init__(self, models_dir: str = "ml/models"):
        self.feature_engineer = FeatureEngineer()
        self._models_dir = Path(models_dir)
        self._model = None
        self._scaler = None
        self._encoders = None
        self._feature_cols = None
        self._load_model()

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _load_model(self):
        """Load trained salary model and preprocessing artifacts."""
        try:
            model_path = self._models_dir / "salary_model.pkl"
            scaler_path = self._models_dir / "salary_scaler.pkl"
            encoders_path = self._models_dir / "salary_encoders.pkl"
            feature_cols_path = self._models_dir / "salary_feature_cols.pkl"

            if all(p.exists() for p in [model_path, scaler_path, encoders_path, feature_cols_path]):
                self._model = joblib.load(model_path)
                self._scaler = joblib.load(scaler_path)
                self._encoders = joblib.load(encoders_path)
                self._feature_cols = joblib.load(feature_cols_path)
                logger.info("Loaded trained salary model (v2)")
            else:
                missing = [p.name for p in [model_path, scaler_path, encoders_path, feature_cols_path] if not p.exists()]
                logger.warning(f"Missing model files: {missing} — run `python -m ml.train_pipeline` to train")
        except Exception as e:
            logger.error(f"Failed to load salary model: {e}")

    @property
    def model_available(self) -> bool:
        return self._model is not None

    # ------------------------------------------------------------------
    # Model prediction
    # ------------------------------------------------------------------

    def _predict_salary_with_model(
        self,
        profession: str,
        career_field: str,
        position_level: str,
        education_level: str,
        location_type: str,
        age: int,
        years_experience: float,
        has_remote: bool,
        is_career_change: bool,
        industry_growth_rate: float,
    ) -> Optional[float]:
        """
        Predict salary using the trained XGBoost model.

        Returns None if the model is unavailable, allowing the caller
        to fall back to formula-based estimation.
        """
        if not self.model_available:
            return None

        is_training_career = int(profession in TRAINING_CAREERS) if profession else 0
        in_training = 0
        if is_training_career and profession:
            tc = TRAINING_CAREERS[profession]
            in_training = int(years_experience < tc["training_years"])

        row = {
            "profession": profession or "other",
            "career_field": career_field,
            "position_level": position_level,
            "education_level": education_level,
            "location_type": location_type,
            "age": age,
            "years_experience": round(years_experience, 1),
            "has_remote": int(has_remote),
            "is_career_change": int(is_career_change),
            "is_training_career": is_training_career,
            "in_training": in_training,
            "industry_growth_rate": round(industry_growth_rate, 4),
        }

        # Encode categoricals using the same encoders from training
        for col in ["career_field", "position_level", "education_level", "location_type", "profession"]:
            le = self._encoders[col]
            val = row[col]
            if val in le.classes_:
                row[col + "_enc"] = le.transform([val])[0]
            else:
                # Unseen label — use median encoded value as fallback
                row[col + "_enc"] = int(np.median(le.transform(le.classes_)))

        features = pd.DataFrame([{c: row[c] for c in self._feature_cols}])
        features_scaled = pd.DataFrame(
            self._scaler.transform(features),
            columns=self._feature_cols,
        )

        prediction = self._model.predict(features_scaled)[0]
        return max(20000, float(prediction))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict_timeline(
        self,
        input_data: MLPredictionInput,
        years: int = 10,
        start_year: int = None,
    ) -> MLPredictionResult:
        """Generate predictions for a multi-year timeline."""
        if start_year is None:
            start_year = datetime.now().year

        predictions = []
        current_state = self._initialize_state(input_data)

        for year_offset in range(years):
            year = start_year + year_offset
            yearly_pred = self._predict_year(input_data, current_state, year, year_offset)
            predictions.append(yearly_pred)
            current_state = self._update_state(current_state, yearly_pred, input_data)

        confidence = self._calculate_confidence(input_data)

        return MLPredictionResult(
            predictions=predictions,
            confidence_score=confidence,
            model_version=self.MODEL_VERSION if self.model_available else "1.0.0-fallback",
            prediction_metadata={
                "input_features": self.feature_engineer.encode_categorical_features(input_data),
                "start_year": start_year,
                "years_predicted": years,
                "model_used": self.model_available,
            },
        )

    # ------------------------------------------------------------------
    # Internal — state management
    # ------------------------------------------------------------------

    def _initialize_state(self, input_data: MLPredictionInput) -> Dict[str, Any]:
        """Initialize the state for year 0."""
        initial_salary = self._predict_salary_for_year(input_data, year_offset=0)
        work_life_balance = self.feature_engineer.calculate_work_life_balance(input_data)

        location_value = input_data.location_type
        if hasattr(location_value, "value"):
            location_value = location_value.value

        return {
            "current_salary": initial_salary,
            "position_level": input_data.position_level,
            "years_in_position": 0,
            "total_experience": input_data.years_experience,
            "work_life_balance": work_life_balance,
            "location": location_value,
            "promotions_received": 0,
            "performance_score": 7.0,
            "career_stability": self.feature_engineer.calculate_career_stability(input_data),
            "detected_profession": input_data.detected_profession,
        }

    # ------------------------------------------------------------------
    # Internal — yearly prediction
    # ------------------------------------------------------------------

    def _predict_year(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        year: int,
        year_offset: int,
    ) -> YearlyPrediction:
        career_metrics = self._predict_career_metrics(input_data, state, year_offset)
        life_quality = self._predict_life_quality(input_data, state, career_metrics, year_offset)
        events = self._predict_major_events(input_data, state, year_offset)

        return YearlyPrediction(
            year=year,
            career_metrics=career_metrics,
            life_quality=life_quality,
            major_event_probability=events,
            location=state["location"],
        )

    # ------------------------------------------------------------------
    # Salary prediction — model-first with formula fallback
    # ------------------------------------------------------------------

    def _predict_salary_for_year(
        self,
        input_data: MLPredictionInput,
        year_offset: int,
        position_level: str = None,
    ) -> float:
        """
        Predict salary for a given year using the trained model.

        Falls back to formula-based estimation if the model is unavailable.
        """
        if position_level is None:
            position_level = input_data.position_level

        career_field = FeatureEngineer._get_key(input_data.career_field)
        education_level = FeatureEngineer._get_key(input_data.education_level)
        location_type = FeatureEngineer._get_key(input_data.location_type)

        model_salary = self._predict_salary_with_model(
            profession=input_data.detected_profession,
            career_field=career_field,
            position_level=position_level,
            education_level=education_level,
            location_type=location_type,
            age=input_data.age + year_offset,
            years_experience=input_data.years_experience + year_offset,
            has_remote=input_data.has_remote_option,
            is_career_change=input_data.is_career_change,
            industry_growth_rate=input_data.industry_growth_rate,
        )

        if model_salary is not None:
            # Blend with current salary if available (keeps predictions grounded)
            if input_data.current_salary and year_offset == 0:
                model_salary = model_salary * 0.6 + input_data.current_salary * 0.4
            return model_salary

        # Fallback: formula-based estimation
        return self._fallback_salary(input_data, year_offset)

    def _fallback_salary(self, input_data: MLPredictionInput, year_offset: int) -> float:
        """Formula-based salary estimation when model is unavailable."""
        base = self.feature_engineer.calculate_base_salary(input_data)
        growth_rate = 0.03 + input_data.industry_growth_rate
        return base * ((1 + growth_rate) ** year_offset)

    # ------------------------------------------------------------------
    # Career metrics
    # ------------------------------------------------------------------

    def _predict_career_metrics(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        year_offset: int,
    ) -> CareerMetrics:
        salary = self._predict_salary_for_year(
            input_data, year_offset, position_level=state["position_level"]
        )

        promotion_prob = self.feature_engineer.calculate_promotion_probability(
            input_data,
            state["years_in_position"],
            state["performance_score"],
        )

        position_title = self._generate_position_title(
            input_data.career_field,
            state["position_level"],
            state["total_experience"] + year_offset,
            input_data.detected_profession,
            year_offset,
        )

        stability = state["career_stability"]
        if year_offset > 2:
            stability = min(10.0, stability + 0.3 * year_offset)

        satisfaction = self.feature_engineer.calculate_job_satisfaction(
            input_data, state["work_life_balance"]
        )
        if input_data.is_career_change and year_offset < 3:
            satisfaction -= (3 - year_offset) * 0.3
        elif year_offset > 5:
            satisfaction += min(1.0, (year_offset - 5) * 0.1)

        work_life_balance = state["work_life_balance"]
        stress = self.feature_engineer.calculate_stress_level(input_data, work_life_balance)

        return CareerMetrics(
            salary=round(salary, 2),
            promotion_probability=round(promotion_prob, 3),
            position_title=position_title,
            career_stability=round(stability, 1),
            job_satisfaction=round(max(1.0, min(10.0, satisfaction)), 1),
            work_life_balance=round(work_life_balance, 1),
            stress_level=round(stress, 1),
        )

    # ------------------------------------------------------------------
    # Life quality metrics
    # ------------------------------------------------------------------

    def _predict_life_quality(
        self,
        input_data: MLPredictionInput,
        state: Dict[str, Any],
        career_metrics: CareerMetrics,
        year_offset: int,
    ) -> LifeQualityMetrics:
        current_age = input_data.age + year_offset

        financial_security = self.feature_engineer.calculate_financial_security(
            career_metrics.salary, current_age, input_data.location_type
        )
        health = self.feature_engineer.calculate_health_score(
            current_age, career_metrics.stress_level,
            career_metrics.work_life_balance, financial_security,
        )
        relationship = self._predict_relationship_quality(
            career_metrics.work_life_balance, career_metrics.stress_level,
            state["career_stability"], year_offset,
        )
        personal_growth = self._predict_personal_growth(
            career_metrics.job_satisfaction, input_data.is_career_change, year_offset,
        )

        happiness = (
            career_metrics.job_satisfaction * 0.25
            + financial_security * 0.20
            + health * 0.20
            + relationship * 0.20
            + personal_growth * 0.15
        )

        return LifeQualityMetrics(
            happiness_score=round(max(1.0, min(10.0, happiness)), 1),
            financial_security=round(financial_security, 1),
            health_score=round(health, 1),
            relationship_quality=round(relationship, 1),
            personal_growth=round(personal_growth, 1),
        )

    def _predict_relationship_quality(
        self, work_life_balance: float, stress_level: float,
        career_stability: float, year_offset: int,
    ) -> float:
        base_quality = work_life_balance * 0.6 + (10 - stress_level) * 0.3 + career_stability * 0.1
        time_factor = min(1.5, 1 + year_offset * 0.05)
        quality = base_quality * time_factor + random.uniform(-0.5, 0.5)
        return max(1.0, min(10.0, quality))

    def _predict_personal_growth(
        self, job_satisfaction: float, is_career_change: bool, year_offset: int,
    ) -> float:
        if is_career_change and year_offset < 3:
            base_growth = 8.5 - year_offset * 0.5
        else:
            base_growth = 7.0
        growth = base_growth * 0.5 + job_satisfaction * 0.5
        if year_offset > 5 and not is_career_change:
            growth -= (year_offset - 5) * 0.2
        growth += random.uniform(-0.3, 0.3)
        return max(1.0, min(10.0, growth))

    # ------------------------------------------------------------------
    # Major events
    # ------------------------------------------------------------------

    def _predict_major_events(
        self, input_data: MLPredictionInput, state: Dict[str, Any], year_offset: int,
    ) -> Dict[str, float]:
        events = {}

        promotion_prob = self.feature_engineer.calculate_promotion_probability(
            input_data, state["years_in_position"], state["performance_score"],
        )
        if promotion_prob > 0.1:
            events["promotion"] = promotion_prob

        if state.get("job_satisfaction", 7) < 5:
            events["job_change"] = 0.15 + (5 - state.get("job_satisfaction", 7)) * 0.05

        if input_data.is_location_change and year_offset < 2:
            events["relocation"] = 0.05
        elif year_offset > 5:
            events["relocation"] = 0.08

        financial_security = state.get("financial_security", 5)
        if financial_security > 7:
            events["major_purchase"] = 0.12

        total_exp = state["total_experience"] + year_offset
        if total_exp % 5 == 0 and total_exp > 0:
            events["career_milestone"] = 0.6

        return events

    # ------------------------------------------------------------------
    # State update
    # ------------------------------------------------------------------

    def _update_state(
        self, state: Dict[str, Any], prediction: YearlyPrediction,
        input_data: MLPredictionInput,
    ) -> Dict[str, Any]:
        new_state = state.copy()
        new_state["current_salary"] = prediction.career_metrics.salary

        if random.random() < prediction.career_metrics.promotion_probability:
            new_state = self._apply_promotion(new_state, input_data)
        else:
            new_state["years_in_position"] += 1

        new_state["total_experience"] += 1
        performance_change = random.uniform(-0.5, 0.5)
        new_state["performance_score"] = max(4.0, min(10.0,
            new_state["performance_score"] + performance_change
        ))
        new_state["work_life_balance"] = prediction.career_metrics.work_life_balance
        new_state["career_stability"] = prediction.career_metrics.career_stability
        return new_state

    def _apply_promotion(self, state: Dict[str, Any], input_data: MLPredictionInput) -> Dict[str, Any]:
        current_idx = POSITION_LEVELS.index(state["position_level"])
        if current_idx < len(POSITION_LEVELS) - 1:
            new_state = state.copy()
            new_state["position_level"] = POSITION_LEVELS[current_idx + 1]
            new_state["years_in_position"] = 0
            new_state["promotions_received"] += 1
            # Re-predict salary at new level via model
            new_salary = self._predict_salary_for_year(
                input_data,
                year_offset=int(new_state["total_experience"] - input_data.years_experience),
                position_level=new_state["position_level"],
            )
            # Ensure promotion is at least a 10% raise
            new_state["current_salary"] = max(new_salary, state["current_salary"] * 1.10)
            new_state["work_life_balance"] = max(3.0, new_state["work_life_balance"] - 0.5)
            return new_state
        return state

    # ------------------------------------------------------------------
    # Position titles (unchanged — data-driven from profession_data.py)
    # ------------------------------------------------------------------

    def _generate_position_title(
        self, career_field: CareerField, position_level: str,
        years_experience: float, detected_profession: str = None,
        year_offset: int = 0,
    ) -> str:
        if detected_profession:
            training_config = get_training_config(detected_profession)
            if training_config:
                return get_training_career_title(detected_profession, year_offset, training_config)
            profession_titles = get_profession_titles_by_level(detected_profession)
            if profession_titles:
                return profession_titles.get(position_level, profession_titles.get("entry"))

        titles = {
            CareerField.TECHNOLOGY: {
                "entry": "Software Engineer I", "mid": "Software Engineer II",
                "senior": "Senior Software Engineer", "lead": "Engineering Manager",
                "executive": "VP of Engineering",
            },
            CareerField.FINANCE: {
                "entry": "Financial Analyst", "mid": "Senior Financial Analyst",
                "senior": "Finance Manager", "lead": "Director of Finance",
                "executive": "Chief Financial Officer",
            },
            CareerField.HEALTHCARE: {
                "entry": "Healthcare Professional", "mid": "Senior Healthcare Professional",
                "senior": "Department Head", "lead": "Medical Director",
                "executive": "Chief Medical Officer",
            },
            CareerField.ENGINEERING: {
                "entry": "Engineer I", "mid": "Engineer II",
                "senior": "Senior Engineer", "lead": "Principal Engineer",
                "executive": "VP of Engineering",
            },
            CareerField.EDUCATION: {
                "entry": "Teacher", "mid": "Senior Teacher",
                "senior": "Department Chair", "lead": "Assistant Principal",
                "executive": "Principal",
            },
            CareerField.BUSINESS: {
                "entry": "Business Analyst", "mid": "Senior Business Analyst",
                "senior": "Business Manager", "lead": "Director",
                "executive": "VP of Operations",
            },
            CareerField.CREATIVE: {
                "entry": "Junior Designer", "mid": "Designer",
                "senior": "Senior Designer", "lead": "Design Lead",
                "executive": "Creative Director",
            },
            CareerField.SERVICE: {
                "entry": "Service Representative", "mid": "Senior Service Representative",
                "senior": "Service Manager", "lead": "Regional Manager",
                "executive": "Director of Operations",
            },
            CareerField.OTHER: {
                "entry": "Associate", "mid": "Senior Associate",
                "senior": "Manager", "lead": "Senior Manager",
                "executive": "Director",
            },
        }
        return titles[career_field][position_level]

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def _calculate_confidence(self, input_data: MLPredictionInput) -> float:
        confidence = 0.85 if self.model_available else 0.65
        if input_data.current_salary:
            confidence += 0.05
        if input_data.years_experience > 3:
            confidence += 0.05
        if input_data.is_career_change:
            confidence -= 0.10
        if input_data.is_location_change:
            confidence -= 0.05
        if input_data.detected_profession:
            confidence += 0.05
        return max(0.5, min(1.0, confidence))
