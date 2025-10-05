"""
ML Integration Service

Integrates ML predictions with AI-generated life simulations for more realistic results.
"""

import logging
from typing import Dict, Any, List

from models.simulation import SimulationRequest, TimelinePoint, UserContext
from models.ml_models import (
    MLPredictionInput, CareerField, EducationLevel, LocationType, MLPredictionResult
)
from ml.prediction_service import MLPredictionService

logger = logging.getLogger(__name__)

class MLIntegrationService:
    """Service to integrate ML predictions with simulations"""

    def __init__(self):
        self.ml_service = MLPredictionService()

    def convert_simulation_to_ml_input(
        self,
        choice: Dict[str, Any],
        user_context: UserContext
    ) -> MLPredictionInput:
        """
        Convert simulation request to ML prediction input

        Args:
            choice: LifeChoice dict (choice_a or choice_b)
            user_context: User's current context

        Returns:
            MLPredictionInput for ML models
        """

        # Map category to career field
        category = choice.get("category", "other").lower()
        career_field = self._map_category_to_field(category)

        # Parse education level
        education = self._parse_education_level(user_context.education_level)

        # Determine location type
        location_type = self._parse_location_type(user_context.current_location)

        # Calculate years of experience from age and education
        age = int(user_context.age) if user_context.age else 30
        years_experience = max(0, age - 22)  # Assume work started at 22

        # Parse current salary
        current_salary = None
        if user_context.current_salary:
            try:
                # Remove currency symbols and commas
                salary_str = str(user_context.current_salary).replace('$', '').replace(',', '').strip()
                current_salary = float(salary_str)
            except (ValueError, AttributeError):
                current_salary = None

        # Determine position level from choice description
        position_level = self._infer_position_level(choice.get("description", ""), years_experience)

        # Determine if career/location change
        is_career_change = "career" in category or "job" in choice.get("title", "").lower()
        is_location_change = "location" in category or "move" in choice.get("title", "").lower()

        # Industry growth rate (can be enhanced with real data)
        industry_growth_rate = self._get_industry_growth_rate(career_field)

        # Remote work option (check description)
        has_remote = "remote" in choice.get("description", "").lower()

        return MLPredictionInput(
            age=age,
            education_level=education,
            years_experience=years_experience,
            current_salary=current_salary,
            career_field=career_field,
            position_level=position_level,
            location_type=location_type,
            is_career_change=is_career_change,
            is_location_change=is_location_change,
            industry_growth_rate=industry_growth_rate,
            has_remote_option=has_remote
        )

    def generate_ml_enhanced_timeline(
        self,
        choice: Dict[str, Any],
        user_context: UserContext
    ) -> List[TimelinePoint]:
        """
        Generate realistic timeline using ML predictions

        Args:
            choice: LifeChoice dict
            user_context: User context

        Returns:
            List of TimelinePoint with ML-predicted values
        """

        try:
            # Convert to ML input
            ml_input = self.convert_simulation_to_ml_input(choice, user_context)

            # Get ML predictions
            ml_result = self.ml_service.predict_timeline(ml_input, years=10)

            # Convert ML predictions to TimelinePoint format
            timeline = []
            for yearly_pred in ml_result.predictions:
                timeline.append(TimelinePoint(
                    year=yearly_pred.year,
                    salary=yearly_pred.career_metrics.salary,
                    happiness_score=yearly_pred.life_quality.happiness_score,
                    major_event=self._select_major_event(yearly_pred.major_event_probability),
                    location=yearly_pred.location,
                    career_title=yearly_pred.career_metrics.position_title
                ))

            logger.info(f"Generated ML-enhanced timeline with {len(timeline)} years")
            return timeline

        except Exception as e:
            logger.error(f"Error generating ML timeline: {e}")
            # Fallback to simple timeline
            return self._generate_fallback_timeline(choice, user_context)

    def get_detailed_ml_predictions(
        self,
        choice: Dict[str, Any],
        user_context: UserContext
    ) -> MLPredictionResult:
        """
        Get full ML prediction result with all metrics

        Useful for premium advanced simulations

        Args:
            choice: LifeChoice dict
            user_context: User context

        Returns:
            Complete MLPredictionResult
        """
        ml_input = self.convert_simulation_to_ml_input(choice, user_context)
        return self.ml_service.predict_timeline(ml_input, years=10)

    def _map_category_to_field(self, category: str) -> CareerField:
        """Map simulation category to career field"""
        category_map = {
            "career": CareerField.BUSINESS,
            "job": CareerField.BUSINESS,
            "technology": CareerField.TECHNOLOGY,
            "tech": CareerField.TECHNOLOGY,
            "software": CareerField.TECHNOLOGY,
            "healthcare": CareerField.HEALTHCARE,
            "health": CareerField.HEALTHCARE,
            "medical": CareerField.HEALTHCARE,
            "finance": CareerField.FINANCE,
            "banking": CareerField.FINANCE,
            "engineering": CareerField.ENGINEERING,
            "education": CareerField.EDUCATION,
            "teaching": CareerField.EDUCATION,
            "business": CareerField.BUSINESS,
            "management": CareerField.BUSINESS,
            "creative": CareerField.CREATIVE,
            "design": CareerField.CREATIVE,
            "art": CareerField.CREATIVE,
            "service": CareerField.SERVICE,
            "hospitality": CareerField.SERVICE,
        }

        for key, field in category_map.items():
            if key in category.lower():
                return field

        return CareerField.OTHER

    def _parse_education_level(self, education: str) -> EducationLevel:
        """Parse education level string"""
        if not education:
            return EducationLevel.BACHELORS  # Default

        education_lower = education.lower()

        if "phd" in education_lower or "doctorate" in education_lower:
            return EducationLevel.PHD
        elif "master" in education_lower or "mba" in education_lower:
            return EducationLevel.MASTERS
        elif "bachelor" in education_lower or "bs" in education_lower or "ba" in education_lower:
            return EducationLevel.BACHELORS
        elif "associate" in education_lower:
            return EducationLevel.ASSOCIATES
        elif "high school" in education_lower or "diploma" in education_lower:
            return EducationLevel.HIGH_SCHOOL
        elif "bootcamp" in education_lower:
            return EducationLevel.BOOTCAMP
        elif "self" in education_lower:
            return EducationLevel.SELF_TAUGHT

        return EducationLevel.BACHELORS

    def _parse_location_type(self, location: str) -> LocationType:
        """Parse location string to type"""
        if not location:
            return LocationType.SUBURB  # Default

        location_lower = location.lower()

        major_cities = ["new york", "los angeles", "chicago", "houston", "phoenix",
                       "philadelphia", "san francisco", "seattle", "boston", "miami",
                       "london", "tokyo", "paris", "singapore"]

        for city in major_cities:
            if city in location_lower:
                return LocationType.MAJOR_CITY

        if any(word in location_lower for word in ["suburb", "suburban"]):
            return LocationType.SUBURB
        elif any(word in location_lower for word in ["rural", "country", "small town"]):
            return LocationType.RURAL
        elif any(word in location_lower for word in ["international", "abroad", "overseas"]):
            return LocationType.INTERNATIONAL

        return LocationType.SMALL_CITY

    def _infer_position_level(self, description: str, years_experience: float) -> str:
        """Infer position level from description and experience"""

        description_lower = description.lower()

        # Check for explicit level mentions
        if any(word in description_lower for word in ["ceo", "cto", "vp", "executive", "director"]):
            return "executive"
        elif any(word in description_lower for word in ["lead", "principal", "staff"]):
            return "lead"
        elif any(word in description_lower for word in ["senior", "sr."]):
            return "senior"
        elif any(word in description_lower for word in ["junior", "jr.", "entry"]):
            return "entry"

        # Infer from experience
        if years_experience < 3:
            return "entry"
        elif years_experience < 6:
            return "mid"
        elif years_experience < 10:
            return "senior"
        elif years_experience < 15:
            return "lead"
        else:
            return "executive"

    def _get_industry_growth_rate(self, career_field: CareerField) -> float:
        """Get estimated industry growth rate"""
        growth_rates = {
            CareerField.TECHNOLOGY: 0.08,  # 8% - high growth
            CareerField.HEALTHCARE: 0.06,  # 6% - strong growth
            CareerField.FINANCE: 0.04,     # 4% - moderate growth
            CareerField.ENGINEERING: 0.05, # 5% - moderate growth
            CareerField.EDUCATION: 0.02,   # 2% - slow growth
            CareerField.BUSINESS: 0.04,    # 4% - moderate growth
            CareerField.CREATIVE: 0.03,    # 3% - modest growth
            CareerField.SERVICE: 0.03,     # 3% - modest growth
            CareerField.OTHER: 0.03        # 3% - default
        }
        return growth_rates.get(career_field, 0.03)

    def _select_major_event(self, event_probabilities: Dict[str, float]) -> str:
        """Select most likely major event from probabilities"""
        if not event_probabilities:
            return None

        # Get event with highest probability (if > 50%)
        max_event = max(event_probabilities.items(), key=lambda x: x[1])
        if max_event[1] > 0.5:
            return max_event[0].replace('_', ' ').title()

        return None

    def _generate_fallback_timeline(
        self,
        choice: Dict[str, Any],
        user_context: UserContext
    ) -> List[TimelinePoint]:
        """Generate simple fallback timeline if ML fails"""

        base_salary = 70000
        if user_context.current_salary:
            try:
                salary_str = str(user_context.current_salary).replace('$', '').replace(',', '').strip()
                base_salary = float(salary_str)
            except:
                pass

        timeline = []
        for i in range(10):
            year = 2025 + i
            salary = base_salary * (1.05 ** i)  # 5% annual growth
            happiness = 7.0 + (i * 0.1) if i < 5 else 7.5  # Initial growth, then plateau

            timeline.append(TimelinePoint(
                year=year,
                salary=salary,
                happiness_score=min(10.0, happiness),
                major_event=None,
                location=user_context.current_location,
                career_title=choice.get("title", "Professional")
            ))

        logger.warning("Using fallback timeline generation")
        return timeline
