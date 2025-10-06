"""
Feature Engineering for ML Pipeline

Transforms raw user input into features suitable for ML models.
"""

import numpy as np
from typing import Dict, Any, List
from models.ml_models import (
    MLPredictionInput, CareerField, EducationLevel, LocationType
)

class FeatureEngineer:
    """Feature engineering for prediction models"""

    # Salary multipliers based on education level
    EDUCATION_SALARY_MULTIPLIER = {
        EducationLevel.HIGH_SCHOOL: 0.7,
        EducationLevel.ASSOCIATES: 0.85,
        EducationLevel.BOOTCAMP: 0.9,
        EducationLevel.SELF_TAUGHT: 0.85,
        EducationLevel.BACHELORS: 1.0,
        EducationLevel.MASTERS: 1.25,
        EducationLevel.PHD: 1.4
    }

    # Base salaries by career field and position level (in USD)
    BASE_SALARIES = {
        CareerField.TECHNOLOGY: {
            "entry": 65000,
            "mid": 95000,
            "senior": 140000,
            "lead": 180000,
            "executive": 250000
        },
        CareerField.FINANCE: {
            "entry": 60000,
            "mid": 90000,
            "senior": 130000,
            "lead": 170000,
            "executive": 300000
        },
        CareerField.HEALTHCARE: {
            "entry": 55000,
            "mid": 80000,
            "senior": 120000,
            "lead": 160000,
            "executive": 220000
        },
        CareerField.ENGINEERING: {
            "entry": 62000,
            "mid": 88000,
            "senior": 125000,
            "lead": 165000,
            "executive": 230000
        },
        CareerField.EDUCATION: {
            "entry": 40000,
            "mid": 55000,
            "senior": 75000,
            "lead": 95000,
            "executive": 130000
        },
        CareerField.BUSINESS: {
            "entry": 50000,
            "mid": 75000,
            "senior": 110000,
            "lead": 150000,
            "executive": 220000
        },
        CareerField.CREATIVE: {
            "entry": 42000,
            "mid": 62000,
            "senior": 90000,
            "lead": 120000,
            "executive": 180000
        },
        CareerField.SERVICE: {
            "entry": 30000,
            "mid": 42000,
            "senior": 60000,
            "lead": 80000,
            "executive": 120000
        },
        CareerField.OTHER: {
            "entry": 45000,
            "mid": 65000,
            "senior": 90000,
            "lead": 120000,
            "executive": 170000
        }
    }

    # Cost of living multipliers by location
    LOCATION_COL_MULTIPLIER = {
        LocationType.MAJOR_CITY: 1.3,
        LocationType.SUBURB: 1.1,
        LocationType.SMALL_CITY: 0.95,
        LocationType.RURAL: 0.8,
        LocationType.INTERNATIONAL: 1.0  
    }

    # Job satisfaction factors by career field
    FIELD_SATISFACTION = {
        CareerField.TECHNOLOGY: 7.5,
        CareerField.HEALTHCARE: 7.2,
        CareerField.FINANCE: 6.8,
        CareerField.ENGINEERING: 7.3,
        CareerField.EDUCATION: 7.0,
        CareerField.BUSINESS: 6.9,
        CareerField.CREATIVE: 7.8,
        CareerField.SERVICE: 6.5,
        CareerField.OTHER: 7.0
    }

    @staticmethod
    def calculate_base_salary(input_data: MLPredictionInput) -> float:
        """Calculate base salary from input features"""
        base = FeatureEngineer.BASE_SALARIES[input_data.career_field][input_data.position_level]

        # Apply education multiplier
        education_mult = FeatureEngineer.EDUCATION_SALARY_MULTIPLIER[input_data.education_level]

        # Apply location multiplier
        location_mult = FeatureEngineer.LOCATION_COL_MULTIPLIER[input_data.location_type]

        # Apply experience boost (2% per year, capped at 50%)
        experience_mult = 1 + min(0.5, input_data.years_experience * 0.02)

        # Remote work bonus (10% for high-demand fields)
        remote_mult = 1.1 if input_data.has_remote_option and input_data.career_field in [
            CareerField.TECHNOLOGY, CareerField.FINANCE, CareerField.BUSINESS
        ] else 1.0

        salary = base * education_mult * location_mult * experience_mult * remote_mult

        # If user has current salary, blend it with calculated (70% calculated, 30% current)
        if input_data.current_salary:
            salary = salary * 0.7 + input_data.current_salary * 0.3

        return round(salary, 2)

    @staticmethod
    def calculate_career_stability(input_data: MLPredictionInput) -> float:
        """Calculate career stability score (1-10)"""
        # Base stability by field
        stability_map = {
            CareerField.TECHNOLOGY: 7.5,
            CareerField.HEALTHCARE: 8.5,
            CareerField.FINANCE: 7.0,
            CareerField.ENGINEERING: 8.0,
            CareerField.EDUCATION: 8.2,
            CareerField.BUSINESS: 7.0,
            CareerField.CREATIVE: 6.0,
            CareerField.SERVICE: 5.5,
            CareerField.OTHER: 6.5
        }

        stability = stability_map[input_data.career_field]

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
        base_satisfaction = FeatureEngineer.FIELD_SATISFACTION[input_data.career_field]

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
        col_multiplier = FeatureEngineer.LOCATION_COL_MULTIPLIER[location_type]
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

        # Age factor (savings accumulation)
        age_factor = min(1.5, age / 100)  # Older = more savings

        return min(10.0, base_security * age_factor)

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
        features = {
            # Education level encoding
            "education_level": input_data.education_level.value,
            "education_numeric": list(EducationLevel).index(input_data.education_level),

            # Career field encoding
            "career_field": input_data.career_field.value,
            "career_numeric": list(CareerField).index(input_data.career_field),

            # Location encoding
            "location_type": input_data.location_type.value,
            "location_numeric": list(LocationType).index(input_data.location_type),

            # Position level encoding
            "position_level": input_data.position_level,
            "position_numeric": ["entry", "mid", "senior", "lead", "executive"].index(
                input_data.position_level
            ),

            # Numerical features
            "age": input_data.age,
            "years_experience": input_data.years_experience,
            "is_career_change": int(input_data.is_career_change),
            "is_location_change": int(input_data.is_location_change),
            "has_remote_option": int(input_data.has_remote_option),
            "industry_growth_rate": input_data.industry_growth_rate,
        }

        return features
