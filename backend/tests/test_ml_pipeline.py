"""
Tests for ML Pipeline

Run with: pytest tests/test_ml_pipeline.py -v
"""

import pytest
from datetime import datetime

from models.ml_models import (
    MLPredictionInput, CareerField, EducationLevel, LocationType,
    CareerMetrics, LifeQualityMetrics, YearlyPrediction
)
from ml.feature_engineering import FeatureEngineer
from ml.prediction_service import MLPredictionService
from services.ml_integration_service import MLIntegrationService
from models.simulation import UserContext

class TestFeatureEngineering:
    """Test feature engineering functions"""

    def test_calculate_base_salary_technology(self):
        """Test salary calculation for technology field"""
        input_data = MLPredictionInput(
            age=25,
            education_level=EducationLevel.BACHELORS,
            years_experience=2,
            career_field=CareerField.TECHNOLOGY,
            position_level="entry",
            location_type=LocationType.MAJOR_CITY
        )

        salary = FeatureEngineer.calculate_base_salary(input_data)

        assert salary > 60000, "Technology entry-level salary should be > 60k"
        assert salary < 120000, "Entry-level salary should be < 120k"

    def test_calculate_base_salary_with_current_salary(self):
        """Test salary calculation when current salary is provided"""
        input_data = MLPredictionInput(
            age=30,
            education_level=EducationLevel.MASTERS,
            years_experience=5,
            current_salary=95000,
            career_field=CareerField.FINANCE,
            position_level="mid",
            location_type=LocationType.SUBURB
        )

        salary = FeatureEngineer.calculate_base_salary(input_data)

        # Should blend with current salary
        assert abs(salary - 95000) < 30000, "Should be close to current salary"

    def test_career_stability_calculation(self):
        """Test career stability score"""
        input_data = MLPredictionInput(
            age=35,
            education_level=EducationLevel.BACHELORS,
            years_experience=10,
            career_field=CareerField.HEALTHCARE,
            position_level="senior",
            location_type=LocationType.SMALL_CITY,
            industry_growth_rate=0.05
        )

        stability = FeatureEngineer.calculate_career_stability(input_data)

        assert 1.0 <= stability <= 10.0, "Stability should be on 1-10 scale"
        assert stability > 7.0, "Healthcare with 10 years experience should have high stability"

    def test_work_life_balance_remote(self):
        """Test work-life balance with remote work"""
        input_data = MLPredictionInput(
            age=28,
            education_level=EducationLevel.BACHELORS,
            years_experience=4,
            career_field=CareerField.TECHNOLOGY,
            position_level="mid",
            location_type=LocationType.SUBURB,
            has_remote_option=True
        )

        balance = FeatureEngineer.calculate_work_life_balance(input_data)

        assert balance > 7.0, "Remote work should improve work-life balance"

    def test_promotion_probability(self):
        """Test promotion probability calculation"""
        input_data = MLPredictionInput(
            age=30,
            education_level=EducationLevel.BACHELORS,
            years_experience=5,
            career_field=CareerField.BUSINESS,
            position_level="mid",
            location_type=LocationType.MAJOR_CITY
        )

        prob = FeatureEngineer.calculate_promotion_probability(
            input_data,
            years_in_position=3,
            performance_score=8.5
        )

        assert 0.0 <= prob <= 1.0, "Probability should be between 0 and 1"
        assert prob > 0.1, "With good performance and time, should have promotion chance"

    def test_financial_security(self):
        """Test financial security calculation"""
        security_high = FeatureEngineer.calculate_financial_security(
            salary=120000,
            age=40,
            location_type=LocationType.SUBURB
        )

        security_low = FeatureEngineer.calculate_financial_security(
            salary=35000,
            age=25,
            location_type=LocationType.MAJOR_CITY
        )

        assert security_high > security_low, "Higher salary should mean more security"
        assert security_high > 7.0, "120k salary should provide high security"
        assert security_low < 6.0, "35k in major city should have lower security"


class TestMLPredictionService:
    """Test ML prediction service"""

    def test_predict_timeline_basic(self):
        """Test basic timeline prediction"""
        service = MLPredictionService()

        input_data = MLPredictionInput(
            age=28,
            education_level=EducationLevel.BACHELORS,
            years_experience=4,
            career_field=CareerField.ENGINEERING,
            position_level="mid",
            location_type=LocationType.SUBURB
        )

        result = service.predict_timeline(input_data, years=10)

        assert len(result.predictions) == 10, "Should predict 10 years"
        assert 0.5 <= result.confidence_score <= 1.0, "Confidence should be reasonable"
        assert result.model_version == "1.0.0-baseline"

    def test_salary_growth_over_time(self):
        """Test that salary grows over time"""
        service = MLPredictionService()

        input_data = MLPredictionInput(
            age=25,
            education_level=EducationLevel.BACHELORS,
            years_experience=1,
            career_field=CareerField.TECHNOLOGY,
            position_level="entry",
            location_type=LocationType.MAJOR_CITY
        )

        result = service.predict_timeline(input_data, years=10)

        salaries = [pred.career_metrics.salary for pred in result.predictions]

        # Check that salaries generally increase
        assert salaries[-1] > salaries[0], "Final salary should be higher than starting"
        assert salaries[4] > salaries[0], "Salary should grow by year 5"

    def test_happiness_metrics_valid(self):
        """Test that happiness metrics are valid"""
        service = MLPredictionService()

        input_data = MLPredictionInput(
            age=30,
            education_level=EducationLevel.MASTERS,
            years_experience=5,
            career_field=CareerField.CREATIVE,
            position_level="senior",
            location_type=LocationType.SMALL_CITY
        )

        result = service.predict_timeline(input_data, years=5)

        for pred in result.predictions:
            lq = pred.life_quality

            assert 1.0 <= lq.happiness_score <= 10.0
            assert 1.0 <= lq.financial_security <= 10.0
            assert 1.0 <= lq.health_score <= 10.0
            assert 1.0 <= lq.relationship_quality <= 10.0
            assert 1.0 <= lq.personal_growth <= 10.0

    def test_career_change_impact(self):
        """Test that career changes affect predictions"""
        service = MLPredictionService()

        # Without career change
        stable_input = MLPredictionInput(
            age=32,
            education_level=EducationLevel.BACHELORS,
            years_experience=8,
            career_field=CareerField.FINANCE,
            position_level="senior",
            location_type=LocationType.MAJOR_CITY,
            is_career_change=False
        )

        # With career change
        change_input = MLPredictionInput(
            age=32,
            education_level=EducationLevel.BACHELORS,
            years_experience=8,
            career_field=CareerField.FINANCE,
            position_level="senior",
            location_type=LocationType.MAJOR_CITY,
            is_career_change=True
        )

        stable_result = service.predict_timeline(stable_input, years=3)
        change_result = service.predict_timeline(change_input, years=3)

        # Career change should initially reduce stability
        assert change_result.predictions[0].career_metrics.career_stability < \
               stable_result.predictions[0].career_metrics.career_stability


class TestMLIntegrationService:
    """Test ML integration with simulation service"""

    def test_convert_simulation_to_ml_input(self):
        """Test conversion from simulation format to ML input"""
        service = MLIntegrationService()

        choice = {
            "title": "Senior Software Engineer",
            "description": "Work at a tech startup with remote options",
            "category": "technology"
        }

        user_context = UserContext(
            age=30,
            current_location="San Francisco",
            current_salary=95000,
            education_level="Bachelor's in Computer Science"
        )

        ml_input = service.convert_simulation_to_ml_input(choice, user_context)

        assert ml_input.career_field == CareerField.TECHNOLOGY
        assert ml_input.age == 30
        assert ml_input.has_remote_option == True
        assert ml_input.current_salary == 95000
        assert ml_input.location_type == LocationType.MAJOR_CITY

    def test_generate_ml_enhanced_timeline(self):
        """Test timeline generation through integration service"""
        service = MLIntegrationService()

        choice = {
            "title": "Product Manager",
            "description": "Lead product development at mid-size company",
            "category": "business"
        }

        user_context = UserContext(
            age=35,
            current_location="Austin",
            current_salary=110000,
            education_level="MBA"
        )

        timeline = service.generate_ml_enhanced_timeline(choice, user_context)

        assert len(timeline) == 10, "Should generate 10-year timeline"
        assert all(hasattr(point, 'salary') for point in timeline)
        assert all(hasattr(point, 'happiness_score') for point in timeline)
        assert all(hasattr(point, 'year') for point in timeline)

    def test_category_mapping(self):
        """Test category to career field mapping"""
        service = MLIntegrationService()

        assert service._map_category_to_field("technology") == CareerField.TECHNOLOGY
        assert service._map_category_to_field("healthcare") == CareerField.HEALTHCARE
        assert service._map_category_to_field("finance") == CareerField.FINANCE
        assert service._map_category_to_field("unknown") == CareerField.OTHER

    def test_education_parsing(self):
        """Test education level parsing"""
        service = MLIntegrationService()

        assert service._parse_education_level("PhD in Physics") == EducationLevel.PHD
        assert service._parse_education_level("Master's Degree") == EducationLevel.MASTERS
        assert service._parse_education_level("Bachelor of Science") == EducationLevel.BACHELORS
        assert service._parse_education_level("High School Diploma") == EducationLevel.HIGH_SCHOOL
        assert service._parse_education_level("Coding Bootcamp") == EducationLevel.BOOTCAMP

    def test_location_parsing(self):
        """Test location type parsing"""
        service = MLIntegrationService()

        assert service._parse_location_type("New York City") == LocationType.MAJOR_CITY
        assert service._parse_location_type("San Francisco") == LocationType.MAJOR_CITY
        assert service._parse_location_type("Suburban Chicago") == LocationType.SUBURB
        assert service._parse_location_type("Rural Montana") == LocationType.RURAL
        assert service._parse_location_type("Paris, France") == LocationType.INTERNATIONAL


class TestIntegration:
    """Integration tests for full ML pipeline"""

    def test_full_simulation_pipeline(self):
        """Test complete simulation flow with ML"""
        from services.ml_integration_service import MLIntegrationService
        from models.simulation import UserContext

        service = MLIntegrationService()

        # Simulate a career decision
        choice_a = {
            "title": "Software Engineer at Google",
            "description": "Join tech giant as senior engineer with remote flexibility",
            "category": "technology"
        }

        choice_b = {
            "title": "Startup CTO",
            "description": "Lead technology at early-stage startup in fintech",
            "category": "technology"
        }

        user_context = UserContext(
            age=32,
            current_location="Seattle",
            current_salary=140000,
            education_level="Master's in CS"
        )

        # Generate timelines
        timeline_a = service.generate_ml_enhanced_timeline(choice_a, user_context)
        timeline_b = service.generate_ml_enhanced_timeline(choice_b, user_context)

        # Verify both timelines generated
        assert len(timeline_a) == 10
        assert len(timeline_b) == 10

        # Verify reasonable values
        assert all(point.salary > 100000 for point in timeline_a), "Google should pay well"
        assert all(1 <= point.happiness_score <= 10 for point in timeline_a)
        assert all(1 <= point.happiness_score <= 10 for point in timeline_b)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
