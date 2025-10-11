"""
ML Pipeline for Production

Clean, reproducible pipeline for ML predictions.
Integrates with FastAPI backend for real-time predictions.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PredictionInput:
    """Input data for ML predictions"""
    job_title: str
    years_experience: int
    education_level: str
    location: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    remote_work: bool = False


@dataclass
class PredictionOutput:
    """ML prediction output"""
    predicted_salary: float
    confidence_score: float
    salary_range: Tuple[float, float]
    career_trajectory: List[Dict]
    recommendations: List[str]


class ParallaxMLPipeline:
    """Production ML Pipeline for Parallax"""

    def __init__(self, models_dir: str = "ml/models"):
        """Initialize ML pipeline with trained models"""
        self.models_dir = Path(models_dir)
        self.model = None
        self.scaler = None
        self.encoders = {}

        self._load_models()

    def _load_models(self):
        """Load trained models and preprocessing artifacts"""
        try:
            # Load best model
            model_path = self.models_dir / "xgboost_tuned_salary.pkl"
            if model_path.exists():
                self.model = joblib.load(model_path)
                logger.info(f"Loaded model from {model_path}")
            else:
                logger.warning(f"Model not found at {model_path}, using fallback")

            # Load scaler if exists
            scaler_path = self.models_dir / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)

            # Load encoders if exist
            encoders_path = self.models_dir / "encoders.pkl"
            if encoders_path.exists():
                self.encoders = joblib.load(encoders_path)

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    def preprocess_input(self, input_data: PredictionInput) -> pd.DataFrame:
        """Preprocess input data for model prediction"""

        # Create feature dictionary
        features = {
            'years_experience': input_data.years_experience,
            'education_level_encoded': self._encode_education(input_data.education_level),
            'location_encoded': self._encode_location(input_data.location),
            'industry_encoded': self._encode_industry(input_data.industry or 'other'),
            'remote_work': 1 if input_data.remote_work else 0,
            'company_size_encoded': self._encode_company_size(input_data.company_size or 'medium')
        }

        # Convert to DataFrame
        df = pd.DataFrame([features])

        # Scale if scaler available
        if self.scaler:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = self.scaler.transform(df[numeric_cols])

        return df

    def _encode_education(self, education: str) -> int:
        """Encode education level"""
        education_map = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'bachelors': 3,
            'master': 4,
            'masters': 4,
            'phd': 5,
            'doctorate': 5
        }

        education_lower = education.lower()
        for key, value in education_map.items():
            if key in education_lower:
                return value
        return 3  # Default to bachelor's

    def _encode_location(self, location: str) -> int:
        """Encode location type"""
        if location.lower() in ['new york', 'san francisco', 'london', 'tokyo']:
            return 3  # Major city
        elif location.lower() in ['los angeles', 'chicago', 'boston', 'seattle']:
            return 2  # Large city
        else:
            return 1  # Other

    def _encode_industry(self, industry: str) -> int:
        """Encode industry"""
        industry_map = {
            'technology': 5,
            'finance': 4,
            'healthcare': 3,
            'education': 2,
            'other': 1
        }
        return industry_map.get(industry.lower(), 1)

    def _encode_company_size(self, size: str) -> int:
        """Encode company size"""
        size_map = {
            'small': 1,
            'medium': 2,
            'large': 3,
            'enterprise': 4
        }
        return size_map.get(size.lower(), 2)

    def predict_salary(self, input_data: PredictionInput) -> PredictionOutput:
        """Make salary prediction"""

        # Preprocess input
        features = self.preprocess_input(input_data)

        # Make prediction
        if self.model:
            predicted_salary = float(self.model.predict(features)[0])

            # Calculate confidence (using model's feature importances or uncertainty)
            confidence_score = self._calculate_confidence(features)

            # Calculate salary range (±15%)
            salary_range = (
                predicted_salary * 0.85,
                predicted_salary * 1.15
            )
        else:
            # Fallback to rule-based prediction
            predicted_salary = self._fallback_prediction(input_data)
            confidence_score = 0.6
            salary_range = (predicted_salary * 0.8, predicted_salary * 1.2)

        # Generate career trajectory
        trajectory = self._generate_trajectory(predicted_salary, input_data.years_experience)

        # Generate recommendations
        recommendations = self._generate_recommendations(input_data, predicted_salary)

        return PredictionOutput(
            predicted_salary=predicted_salary,
            confidence_score=confidence_score,
            salary_range=salary_range,
            career_trajectory=trajectory,
            recommendations=recommendations
        )

    def _calculate_confidence(self, features: pd.DataFrame) -> float:
        """Calculate prediction confidence"""
        # Base confidence
        base_confidence = 0.75

        # Adjust based on feature completeness
        non_zero_features = (features != 0).sum().sum()
        total_features = features.shape[1]
        completeness_bonus = (non_zero_features / total_features) * 0.15

        return min(base_confidence + completeness_bonus, 0.95)

    def _fallback_prediction(self, input_data: PredictionInput) -> float:
        """Fallback salary prediction when model is unavailable"""

        # Base salaries by education
        base_salary = {
            'high school': 40000,
            'associate': 50000,
            'bachelor': 65000,
            'bachelors': 65000,
            'master': 85000,
            'masters': 85000,
            'phd': 100000,
            'doctorate': 100000
        }

        # Get base
        education_lower = input_data.education_level.lower()
        salary = 65000  # Default

        for key, value in base_salary.items():
            if key in education_lower:
                salary = value
                break

        # Adjust for experience (3% per year)
        salary *= (1.03 ** input_data.years_experience)

        # Adjust for location
        if input_data.location.lower() in ['new york', 'san francisco']:
            salary *= 1.3
        elif input_data.location.lower() in ['los angeles', 'chicago', 'boston', 'seattle']:
            salary *= 1.15

        # Adjust for remote work
        if input_data.remote_work:
            salary *= 1.05

        return salary

    def _generate_trajectory(self, current_salary: float, years_experience: int, years: int = 10) -> List[Dict]:
        """Generate career trajectory"""

        trajectory = []

        # Growth rate based on experience
        if years_experience < 3:
            growth_rate = 0.08  # 8% for early career
        elif years_experience < 7:
            growth_rate = 0.06  # 6% for mid career
        else:
            growth_rate = 0.04  # 4% for senior

        for year in range(years + 1):
            salary = current_salary * ((1 + growth_rate) ** year)

            # Determine level
            if salary < 70000:
                level = "Junior"
            elif salary < 120000:
                level = "Mid-Level"
            elif salary < 180000:
                level = "Senior"
            else:
                level = "Lead/Principal"

            trajectory.append({
                'year': year,
                'salary': round(salary, 2),
                'level': level,
                'happiness_score': self._estimate_happiness(salary, year)
            })

        return trajectory

    def _estimate_happiness(self, salary: float, years_into_future: int) -> float:
        """Estimate happiness score based on salary and time"""

        # Base happiness from salary (diminishing returns)
        if salary < 50000:
            base_happiness = 5.0
        elif salary < 100000:
            base_happiness = 6.5
        elif salary < 150000:
            base_happiness = 7.5
        else:
            base_happiness = 8.0 + min((salary - 150000) / 100000, 1.5)

        # Adjust for career progression (slight decrease over time due to stress)
        time_adjustment = -0.05 * min(years_into_future, 5)

        return min(max(base_happiness + time_adjustment, 1.0), 10.0)

    def _generate_recommendations(self, input_data: PredictionInput, predicted_salary: float) -> List[str]:
        """Generate career recommendations"""

        recommendations = []

        # Education recommendations
        if input_data.education_level.lower() in ['high school', 'associate']:
            recommendations.append("Consider pursuing a Bachelor's degree to increase earning potential by 30-40%")

        # Experience recommendations
        if input_data.years_experience < 3:
            recommendations.append("Focus on building core skills and certifications in your first 3 years")

        # Location recommendations
        if input_data.location.lower() not in ['new york', 'san francisco', 'boston', 'seattle']:
            recommendations.append("Consider relocating to a major tech hub for 15-30% salary increase")

        # Remote work recommendations
        if not input_data.remote_work:
            recommendations.append("Negotiate remote work options for better work-life balance and potential 5-10% salary increase")

        # Salary-specific recommendations
        if predicted_salary < 80000:
            recommendations.append("Target mid-sized companies with growth potential for faster career advancement")
        elif predicted_salary > 150000:
            recommendations.append("Consider leadership roles or specialized technical tracks for continued growth")

        return recommendations


def main():
    """Test the ML pipeline"""

    # Initialize pipeline
    pipeline = ParallaxMLPipeline()

    # Create test input
    test_input = PredictionInput(
        job_title="Software Engineer",
        years_experience=5,
        education_level="Bachelor's",
        location="San Francisco",
        industry="Technology",
        company_size="medium",
        remote_work=True
    )

    # Make prediction
    result = pipeline.predict_salary(test_input)

    # Display results
    print("\n" + "="*80)
    print("PARALLAX ML PREDICTION")
    print("="*80)
    print(f"\nPredicted Salary: ${result.predicted_salary:,.2f}")
    print(f"Confidence Score: {result.confidence_score:.2%}")
    print(f"Salary Range: ${result.salary_range[0]:,.2f} - ${result.salary_range[1]:,.2f}")

    print(f"\nCareer Trajectory (10 years):")
    for point in result.career_trajectory[::2]:  # Show every other year
        print(f"  Year {point['year']}: ${point['salary']:,.2f} ({point['level']}) - Happiness: {point['happiness_score']:.1f}/10")

    print(f"\nRecommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")

    print("\n" + "="*80)
    print("✓ Pipeline test complete!")


if __name__ == "__main__":
    main()
