"""
Feature Engineering for ML Pipeline

Transforms raw user input into features suitable for ML models.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from models.ml_models import (
    MLPredictionInput, CareerField, EducationLevel, LocationType
)
from ml.profession_data import (
    get_profession_salary,
    get_training_config,
    PROFESSION_SALARIES
)
from config import (
    LOCATION_MULTIPLIERS,
    EXPERIENCE_MULTIPLIER_PER_YEAR,
    EXPERIENCE_MULTIPLIER_CAP,
    REMOTE_WORK_SALARY_BONUS,
    POST_TRAINING_GROWTH_RATE,
    ANNUAL_TRAINING_RAISE_RATE,
)

class FeatureEngineer:
    """Feature engineering for prediction models"""

    # Salary multipliers based on education level (string keys for compatibility)
    EDUCATION_SALARY_MULTIPLIER = {
        "high_school": 0.7,
        "associates": 0.85,
        "bootcamp": 0.9,
        "self_taught": 0.85,
        "bachelors": 1.0,
        "masters": 1.25,
        "phd": 1.4
    }

    # Base salaries by career field and position level (string keys for compatibility)
    BASE_SALARIES = {
        "technology": {
            "entry": 65000,
            "mid": 95000,
            "senior": 140000,
            "lead": 180000,
            "executive": 250000
        },
        "finance": {
            "entry": 60000,
            "mid": 90000,
            "senior": 130000,
            "lead": 170000,
            "executive": 300000
        },
        "healthcare": {
            "entry": 55000,
            "mid": 80000,
            "senior": 120000,
            "lead": 160000,
            "executive": 220000
        },
        "engineering": {
            "entry": 62000,
            "mid": 88000,
            "senior": 125000,
            "lead": 165000,
            "executive": 230000
        },
        "education": {
            "entry": 40000,
            "mid": 55000,
            "senior": 75000,
            "lead": 95000,
            "executive": 130000
        },
        "business": {
            "entry": 50000,
            "mid": 75000,
            "senior": 110000,
            "lead": 150000,
            "executive": 220000
        },
        "creative": {
            "entry": 42000,
            "mid": 62000,
            "senior": 90000,
            "lead": 120000,
            "executive": 180000
        },
        "service": {
            "entry": 30000,
            "mid": 42000,
            "senior": 60000,
            "lead": 80000,
            "executive": 120000
        },
        "other": {
            "entry": 45000,
            "mid": 65000,
            "senior": 90000,
            "lead": 120000,
            "executive": 170000
        }
    }

    @staticmethod
    def get_location_multiplier(location_type) -> float:
        """Get location multiplier, handling both enum and string types"""
        if hasattr(location_type, 'value'):
            key = location_type.value
        else:
            key = str(location_type).lower()
        return LOCATION_MULTIPLIERS.get(key, 1.0)

    # Job satisfaction factors by career field (string keys)
    FIELD_SATISFACTION = {
        "technology": 7.5,
        "healthcare": 7.2,
        "finance": 6.8,
        "engineering": 7.3,
        "education": 7.0,
        "business": 6.9,
        "creative": 7.8,
        "service": 6.5,
        "other": 7.0
    }

    @staticmethod
    def _get_key(value) -> str:
        """Convert enum or string to lowercase string key"""
        if hasattr(value, 'value'):
            return value.value.lower()
        return str(value).lower()

    @staticmethod
    def calculate_base_salary(input_data: MLPredictionInput) -> float:
        """Calculate base salary from input features, using profession-specific data if available"""

        # Check if a specific profession was detected
        if input_data.detected_profession and input_data.detected_profession in PROFESSION_SALARIES:
            profession_salary = get_profession_salary(
                input_data.detected_profession,
                input_data.position_level
            )
            if profession_salary:
                base = profession_salary
            else:
                # Fallback to entry level for this profession
                base = PROFESSION_SALARIES[input_data.detected_profession].get("entry", 50000)
        else:
            # Use generic career field salary
            career_key = FeatureEngineer._get_key(input_data.career_field)
            base = FeatureEngineer.BASE_SALARIES[career_key][input_data.position_level]

        # Apply education multiplier
        education_key = FeatureEngineer._get_key(input_data.education_level)
        education_mult = FeatureEngineer.EDUCATION_SALARY_MULTIPLIER.get(education_key, 1.0)

        # Apply location multiplier
        location_mult = FeatureEngineer.get_location_multiplier(input_data.location_type)

        # Apply experience boost
        experience_mult = 1 + min(EXPERIENCE_MULTIPLIER_CAP, input_data.years_experience * EXPERIENCE_MULTIPLIER_PER_YEAR)

        # Remote work bonus for high-demand fields
        remote_mult = (1 + REMOTE_WORK_SALARY_BONUS) if input_data.has_remote_option and input_data.career_field in [
            CareerField.TECHNOLOGY, CareerField.FINANCE, CareerField.BUSINESS
        ] else 1.0

        salary = base * education_mult * location_mult * experience_mult * remote_mult

        # If user has current salary, blend it with calculated (70% calculated, 30% current)
        if input_data.current_salary:
            salary = salary * 0.7 + input_data.current_salary * 0.3

        return round(salary, 2)

    @staticmethod
    def calculate_profession_salary_for_year(
        input_data: MLPredictionInput,
        year_offset: int
    ) -> Optional[float]:
        """
        Calculate salary for a specific year, considering training periods.

        For careers like medicine with residency, returns training salary during
        training years and post-training salary afterwards.

        Args:
            input_data: ML prediction input with detected_profession
            year_offset: Years since career start (0 = first year)

        Returns:
            Salary for this year, or None if no profession-specific data
        """
        if not input_data.detected_profession:
            return None

        training_config = get_training_config(input_data.detected_profession)

        if training_config:
            training_years = training_config["training_years"]

            if year_offset < training_years:
                # Still in training (residency, etc.)
                base = training_config["training_salary"]
                annual_raise = training_config.get("annual_training_raise", ANNUAL_TRAINING_RAISE_RATE)
                salary = base * ((1 + annual_raise) ** year_offset)
            else:
                # Post-training - now earning full salary
                years_post = year_offset - training_years
                base = training_config["post_training_salary"]
                salary = base * ((1 + POST_TRAINING_GROWTH_RATE) ** years_post)

            # Apply location multiplier
            location_mult = FeatureEngineer.get_location_multiplier(input_data.location_type)
            salary *= location_mult

            return round(salary, 2)

        # Non-training profession - use standard profession salary with growth
        profession_data = PROFESSION_SALARIES.get(input_data.detected_profession)
        if profession_data:
            base = profession_data.get(input_data.position_level, profession_data.get("entry"))
            # Standard 4% annual growth
            salary = base * ((1.04) ** year_offset)

            # Apply location multiplier
            location_mult = FeatureEngineer.get_location_multiplier(input_data.location_type)
            salary *= location_mult

            return round(salary, 2)

        return None

    @staticmethod
    def calculate_career_stability(input_data: MLPredictionInput) -> float:
        """Calculate career stability score (1-10)"""
        # Base stability by field (string keys)
        stability_map = {
            "technology": 7.5,
            "healthcare": 8.5,
            "finance": 7.0,
            "engineering": 8.0,
            "education": 8.2,
            "business": 7.0,
            "creative": 6.0,
            "service": 5.5,
            "other": 6.5
        }

        career_key = FeatureEngineer._get_key(input_data.career_field)
        stability = stability_map.get(career_key, 6.5)

        # Career change reduces stability temporarily
        if input_data.is_career_change:
            stability -= 2.0

        # Experience increases stability
        stability += min(2.0, input_data.years_experience * 0.1)

        # Industry growth affects stability
        stability += input_data.industry_growth_rate * 10  # Scale to 1-10 range

        return max(1.0, min(10.0, stability))

    @staticmethod
    def calculate_job_satisfaction(input_data: MLPredictionInput, work_life_balance: float) -> float:
        """Calculate job satisfaction score (1-10)"""
        career_key = FeatureEngineer._get_key(input_data.career_field)
        base_satisfaction = FeatureEngineer.FIELD_SATISFACTION.get(career_key, 7.0)

        # Work-life balance strongly affects satisfaction
        satisfaction = base_satisfaction * 0.6 + work_life_balance * 0.4

        # Remote work bonus
        if input_data.has_remote_option:
            satisfaction += 0.5

        # Career change penalty (temporary)
        if input_data.is_career_change:
            satisfaction -= 1.0

        # Location change stress
        if input_data.is_location_change:
            satisfaction -= 0.5

        return max(1.0, min(10.0, satisfaction))

    @staticmethod
    def calculate_work_life_balance(input_data: MLPredictionInput) -> float:
        """Calculate work-life balance score (1-10)"""
        # Base by position level
        level_balance = {
            "entry": 7.0,
            "mid": 6.5,
            "senior": 6.0,
            "lead": 5.5,
            "executive": 4.5
        }

        balance = level_balance.get(input_data.position_level, 6.0)

        # Remote work significantly improves work-life balance
        if input_data.has_remote_option:
            balance += 1.5

        # Career field adjustments
        field_adjustments = {
            CareerField.TECHNOLOGY: 0.5,
            CareerField.HEALTHCARE: -0.5,
            CareerField.FINANCE: -1.0,
            CareerField.EDUCATION: 1.0,
            CareerField.CREATIVE: 0.5,
        }
        balance += field_adjustments.get(input_data.career_field, 0)

        return max(1.0, min(10.0, balance))

    @staticmethod
    def calculate_stress_level(input_data: MLPredictionInput, work_life_balance: float) -> float:
        """Calculate stress level (1-10, 10 = highest stress)"""
        # Inverse of work-life balance
        base_stress = 10 - work_life_balance

        # Position level increases stress
        level_stress = {
            "entry": 0,
            "mid": 0.5,
            "senior": 1.0,
            "lead": 2.0,
            "executive": 3.0
        }
        stress = base_stress + level_stress.get(input_data.position_level, 0)

        # Career/location changes add temporary stress
        if input_data.is_career_change:
            stress += 2.0
        if input_data.is_location_change:
            stress += 1.5

        return max(1.0, min(10.0, stress))

    @staticmethod
    def calculate_promotion_probability(
        input_data: MLPredictionInput,
        years_in_position: int,
        performance_score: float
    ) -> float:
        """Calculate probability of promotion in a given year"""
        # Base promotion rate by position
        base_rates = {
            "entry": 0.25,
            "mid": 0.15,
            "senior": 0.10,
            "lead": 0.05,
            "executive": 0.02
        }

        base_prob = base_rates.get(input_data.position_level, 0.10)

        # Time in position increases probability
        time_factor = min(1.5, 1 + years_in_position * 0.1)

        # Performance affects promotion
        performance_factor = performance_score / 7.0  # Normalize around 7/10 performance

        # Industry growth affects opportunities
        growth_factor = 1 + input_data.industry_growth_rate

        prob = base_prob * time_factor * performance_factor * growth_factor

        return max(0.0, min(1.0, prob))

    @staticmethod
    def calculate_financial_security(salary: float, age: int, location_type: LocationType) -> float:
        """Calculate financial security score (1-10)"""
        # Adjust salary for cost of living
        col_multiplier = FeatureEngineer.get_location_multiplier(location_type)
        adjusted_salary = salary / col_multiplier

        # Income brackets for security
        if adjusted_salary < 40000:
            base_security = 3.0
        elif adjusted_salary < 60000:
            base_security = 5.0
        elif adjusted_salary < 90000:
            base_security = 7.0
        elif adjusted_salary < 150000:
            base_security = 8.5
        else:
            base_security = 9.5

        # Age factor (savings accumulation) - even young workers with high income have security
        age_factor = min(1.3, 0.7 + age * 0.01)

        return max(1.0, min(10.0, base_security * age_factor))

    @staticmethod
    def calculate_health_score(
        age: int,
        stress_level: float,
        work_life_balance: float,
        financial_security: float
    ) -> float:
        """Calculate health score (1-10)"""
        # Base health declines with age
        age_factor = max(5.0, 10 - (age - 30) * 0.05)

        # Stress negatively impacts health
        stress_factor = (10 - stress_level) / 10

        # Work-life balance affects health
        balance_factor = work_life_balance / 10

        # Financial security affects health (reduced stress)
        finance_factor = financial_security / 10

        health = (age_factor * 0.4 +
                 stress_factor * 10 * 0.3 +
                 balance_factor * 10 * 0.2 +
                 finance_factor * 10 * 0.1)

        return max(1.0, min(10.0, health))

    @staticmethod
    def encode_categorical_features(input_data: MLPredictionInput) -> Dict[str, Any]:
        """One-hot encode categorical features for ML models"""
        # Get string values safely
        education_val = FeatureEngineer._get_key(input_data.education_level)
        career_val = FeatureEngineer._get_key(input_data.career_field)
        location_val = FeatureEngineer._get_key(input_data.location_type)

        # Define enum value lists for numeric encoding
        education_levels = ["high_school", "associates", "bachelors", "masters", "phd", "bootcamp", "self_taught"]
        career_fields = ["technology", "healthcare", "finance", "education", "engineering", "business", "creative", "service", "other"]
        location_types = ["major_city", "suburb", "small_city", "rural", "international"]

        features = {
            # Education level encoding
            "education_level": education_val,
            "education_numeric": education_levels.index(education_val) if education_val in education_levels else 2,

            # Career field encoding
            "career_field": career_val,
            "career_numeric": career_fields.index(career_val) if career_val in career_fields else 8,

            # Location encoding
            "location_type": location_val,
            "location_numeric": location_types.index(location_val) if location_val in location_types else 1,

            # Position level encoding
            "position_level": input_data.position_level,
            "position_numeric": ["entry", "mid", "senior", "lead", "executive"].index(
                input_data.position_level
            ) if input_data.position_level in ["entry", "mid", "senior", "lead", "executive"] else 0,

            # Numerical features
            "age": input_data.age,
            "years_experience": input_data.years_experience,
            "is_career_change": int(input_data.is_career_change),
            "is_location_change": int(input_data.is_location_change),
            "has_remote_option": int(input_data.has_remote_option),
            "industry_growth_rate": input_data.industry_growth_rate,
        }

        return features
