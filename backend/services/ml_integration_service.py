"""
ML Integration Service

Integrates ML predictions with AI-generated life simulations for more realistic results.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from models.simulation import SimulationRequest, TimelinePoint, UserContext
from models.ml_models import (
    MLPredictionInput, CareerField, EducationLevel, LocationType, MLPredictionResult
)
from ml.prediction_service import MLPredictionService
from ml.profession_data import (
    detect_profession,
    get_profession_salary,
    get_profession_field,
    get_training_config,
    PROFESSION_SALARIES
)

logger = logging.getLogger(__name__)

class MLIntegrationService:
    """Service to integrate ML predictions with simulations"""

    def __init__(self):
        self.ml_service = MLPredictionService()

    def _detect_profession_from_choice(
        self,
        choice: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[Dict[str, int]]]:
        """
        Detect specific profession from choice title and description.

        Args:
            choice: LifeChoice dict with title and description

        Returns:
            Tuple of (profession_key, salary_data) or (None, None) if not found
        """
        title = choice.get("title", "")
        description = choice.get("description", "")

        profession = detect_profession(title, description)

        if profession and profession in PROFESSION_SALARIES:
            logger.info(f"Detected profession: {profession} from title: {title}")
            return profession, PROFESSION_SALARIES[profession]

        return None, None

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

        # First, try to detect specific profession from title
        detected_profession, profession_salary_data = self._detect_profession_from_choice(choice)

        # Get category (needed for career/location change detection)
        category = choice.get("category", "other").lower()

        # Map category to career field (use profession field if detected)
        if detected_profession:
            career_field = get_profession_field(detected_profession)
        else:
            # Also check title for career field hints
            title = choice.get("title", "").lower()
            career_field = self._map_category_to_field(category, title)

        # Parse education level
        education = self._parse_education_level(user_context.education_level)

        # Determine location type
        location_type = self._parse_location_type(user_context.current_location)

        # Calculate years of experience from age and education
        age = int(user_context.age) if user_context.age else 30
        years_experience = max(0, age - 22)  # Assume work started at 22

        # Determine position level from choice description
        position_level = self._infer_position_level(choice.get("description", ""), years_experience)

        # Parse current salary - use profession-specific salary if detected
        current_salary = None
        if user_context.current_salary:
            try:
                # Remove currency symbols and commas
                salary_str = str(user_context.current_salary).replace('$', '').replace(',', '').strip()
                current_salary = float(salary_str)
            except (ValueError, AttributeError):
                current_salary = None

        # If profession detected and no user salary, use profession-specific base salary
        if detected_profession and profession_salary_data and not current_salary:
            profession_base = profession_salary_data.get(position_level, profession_salary_data.get("entry"))
            current_salary = float(profession_base)
            logger.info(f"Using profession salary for {detected_profession} ({position_level}): ${current_salary:,.0f}")

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
            has_remote_option=has_remote,
            detected_profession=detected_profession
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

    def _map_category_to_field(self, category: str, title: str = "") -> CareerField:
        """Map simulation category or title to career field"""
        # Combine category and title for matching
        combined = f"{category} {title}".lower()

        # Title-based detection takes priority (more specific)
        title_keywords = {
            # Healthcare
            "doctor": CareerField.HEALTHCARE,
            "physician": CareerField.HEALTHCARE,
            "surgeon": CareerField.HEALTHCARE,
            "nurse": CareerField.HEALTHCARE,
            "dentist": CareerField.HEALTHCARE,
            "pharmacist": CareerField.HEALTHCARE,
            "therapist": CareerField.HEALTHCARE,
            "medical": CareerField.HEALTHCARE,

            # Technology
            "software": CareerField.TECHNOLOGY,
            "developer": CareerField.TECHNOLOGY,
            "programmer": CareerField.TECHNOLOGY,
            "engineer": CareerField.TECHNOLOGY,  # Will be overridden if more specific
            "data scientist": CareerField.TECHNOLOGY,
            "devops": CareerField.TECHNOLOGY,
            "cybersecurity": CareerField.TECHNOLOGY,

            # Finance
            "banker": CareerField.FINANCE,
            "accountant": CareerField.FINANCE,
            "financial": CareerField.FINANCE,
            "actuary": CareerField.FINANCE,
            "trader": CareerField.FINANCE,

            # Legal/Business
            "lawyer": CareerField.BUSINESS,
            "attorney": CareerField.BUSINESS,
            "consultant": CareerField.BUSINESS,

            # Education
            "teacher": CareerField.EDUCATION,
            "professor": CareerField.EDUCATION,
            "instructor": CareerField.EDUCATION,

            # Creative
            "designer": CareerField.CREATIVE,
            "artist": CareerField.CREATIVE,
            "writer": CareerField.CREATIVE,
            "photographer": CareerField.CREATIVE,

            # Service
            "chef": CareerField.SERVICE,
            "pilot": CareerField.SERVICE,
            "police": CareerField.SERVICE,
            "firefighter": CareerField.SERVICE,
        }

        # Check title keywords first
        for keyword, field in title_keywords.items():
            if keyword in combined:
                return field

        # Fallback to category-based mapping
        category_map = {
            "career": CareerField.BUSINESS,
            "job": CareerField.BUSINESS,
            "technology": CareerField.TECHNOLOGY,
            "tech": CareerField.TECHNOLOGY,
            "healthcare": CareerField.HEALTHCARE,
            "health": CareerField.HEALTHCARE,
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

        # Check qualifying words first — "suburban Chicago" is a suburb, not a major city
        if any(word in location_lower for word in ["suburb", "suburban"]):
            return LocationType.SUBURB
        elif any(word in location_lower for word in ["rural", "country", "small town"]):
            return LocationType.RURAL
        elif any(word in location_lower for word in ["international", "abroad", "overseas"]):
            return LocationType.INTERNATIONAL

        # International cities — classify as international before checking US major cities
        international_cities = ["london", "tokyo", "paris", "singapore", "berlin",
                               "sydney", "toronto", "mumbai", "shanghai", "dubai"]
        for city in international_cities:
            if city in location_lower:
                return LocationType.INTERNATIONAL

        us_major_cities = ["new york", "los angeles", "chicago", "houston", "phoenix",
                          "philadelphia", "san francisco", "seattle", "boston", "miami"]
        for city in us_major_cities:
            if city in location_lower:
                return LocationType.MAJOR_CITY

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

    def _get_industry_growth_rate(self, career_field) -> float:
        """Get estimated industry growth rate"""
        # Get string key for lookup
        if hasattr(career_field, 'value'):
            key = career_field.value.lower()
        else:
            key = str(career_field).lower()

        growth_rates = {
            "technology": 0.08,  # 8% - high growth
            "healthcare": 0.06,  # 6% - strong growth
            "finance": 0.04,     # 4% - moderate growth
            "engineering": 0.05, # 5% - moderate growth
            "education": 0.02,   # 2% - slow growth
            "business": 0.04,    # 4% - moderate growth
            "creative": 0.03,    # 3% - modest growth
            "service": 0.03,     # 3% - modest growth
            "other": 0.03        # 3% - default
        }
        return growth_rates.get(key, 0.03)

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
            except (ValueError, AttributeError):
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
