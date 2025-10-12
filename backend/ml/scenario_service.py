"""
Scenario Service
Unified service that combines ML scenario simulation and LLM narrative generation.

This is the main entry point for the ML scenario generation pipeline.
"""

from typing import Dict, List, Optional

try:
    from .scenario_simulator import ScenarioSimulator
    from .narrative_generator import NarrativeGenerator
except ImportError:
    from scenario_simulator import ScenarioSimulator
    from narrative_generator import NarrativeGenerator


class ScenarioService:
    """
    Complete scenario generation service combining ML predictions and narratives.

    This service orchestrates:
    1. ML-based scenario simulation
    2. LLM-powered narrative generation
    3. Comparative analysis across scenarios
    """

    def __init__(
        self,
        models_dir: str = "models",
        features_dir: str = "data/features",
        openrouter_api_key: Optional[str] = None
    ):
        """
        Initialize scenario service.

        Args:
            models_dir: Directory containing trained ML models
            features_dir: Directory containing feature engineering data
            openrouter_api_key: OpenRouter API key for LLM narratives
        """
        self.simulator = ScenarioSimulator(models_dir, features_dir)
        self.narrator = NarrativeGenerator(api_key=openrouter_api_key)

    def generate_complete_scenarios(
        self,
        user_profile: Dict,
        years: int = 10,
        include_narratives: bool = True
    ) -> Dict:
        """
        Generate complete scenarios with ML predictions and narratives.

        Args:
            user_profile: User profile containing:
                - age: Current age
                - education: Education level
                - field: Career field
                - experience_years: Years of experience
                - current_salary: Current salary (optional)
                - location_type: urban/suburban/rural
                - remote_work: full/hybrid/none
            years: Number of years to project (default 10)
            include_narratives: Whether to generate LLM narratives (default True)

        Returns:
            Complete scenario package with:
            - scenarios: Timeline data for each scenario type
            - comparisons: Statistical comparisons
            - narratives: Natural language descriptions (if enabled)
            - metadata: Generation info
        """
        # Generate ML scenarios
        scenarios = self.simulator.generate_scenarios(user_profile, years)

        # Generate comparison statistics
        comparisons = self.simulator.compare_scenarios(scenarios)

        # Build response
        result = {
            'user_profile': user_profile,
            'scenarios': {},
            'comparisons': comparisons,
            'metadata': {
                'years_projected': years,
                'scenario_count': len(scenarios),
                'model_type': 'ml_enhanced',
                'has_narratives': include_narratives
            }
        }

        # Process each scenario
        for scenario_type, timeline in scenarios.items():
            scenario_data = {
                'type': scenario_type,
                'timeline': timeline,
                'statistics': comparisons[scenario_type],
            }

            # Add narratives if enabled
            if include_narratives:
                scenario_data['narrative'] = self.narrator.generate_scenario_narrative(
                    user_profile,
                    scenario_type,
                    timeline,
                    comparisons[scenario_type]
                )

                # Add year-by-year narratives for key years
                scenario_data['year_narratives'] = {}
                key_years = [0, len(timeline) // 2, len(timeline) - 1]  # Start, middle, end

                for year_idx in key_years:
                    if year_idx < len(timeline):
                        year_data = timeline[year_idx]
                        scenario_data['year_narratives'][year_data['year']] = \
                            self.narrator.generate_year_narrative(year_data)

            result['scenarios'][scenario_type] = scenario_data

        # Add overall comparison narrative
        if include_narratives:
            result['comparison_narrative'] = self.narrator.generate_comparison_summary(
                user_profile,
                scenarios,
                comparisons
            )

        return result

    def generate_single_scenario(
        self,
        user_profile: Dict,
        scenario_type: str = 'realistic',
        years: int = 10,
        include_narrative: bool = True
    ) -> Dict:
        """
        Generate a single scenario (faster for quick predictions).

        Args:
            user_profile: User profile data
            scenario_type: 'optimistic', 'realistic', or 'pessimistic'
            years: Number of years to project
            include_narrative: Whether to generate narrative

        Returns:
            Single scenario with timeline and optional narrative
        """
        # Generate all scenarios (needed for comparison stats)
        all_scenarios = self.simulator.generate_scenarios(user_profile, years)
        comparisons = self.simulator.compare_scenarios(all_scenarios)

        # Get requested scenario
        timeline = all_scenarios.get(scenario_type, all_scenarios['realistic'])
        stats = comparisons.get(scenario_type, comparisons['realistic'])

        result = {
            'type': scenario_type,
            'timeline': timeline,
            'statistics': stats,
            'user_profile': user_profile
        }

        if include_narrative:
            result['narrative'] = self.narrator.generate_scenario_narrative(
                user_profile,
                scenario_type,
                timeline,
                stats
            )

        return result

    def generate_quick_prediction(
        self,
        user_profile: Dict,
        target_year: int = 5
    ) -> Dict:
        """
        Generate a quick prediction for a specific future year.

        Args:
            user_profile: User profile data
            target_year: Year to predict (1-10)

        Returns:
            Predictions for the target year across all scenarios
        """
        scenarios = self.simulator.generate_scenarios(user_profile, years=target_year)

        predictions = {}
        for scenario_type, timeline in scenarios.items():
            if timeline:
                target_data = timeline[-1]  # Last year is the target
                predictions[scenario_type] = {
                    'age': target_data['age'],
                    'salary': target_data['salary'],
                    'life_satisfaction': target_data['life_satisfaction'],
                    'career_growth_index': target_data['career_growth_index'],
                    'financial_security': target_data['financial_security'],
                    'work_life_balance': target_data['work_life_balance']
                }

        return {
            'target_year': target_year,
            'target_age': user_profile['age'] + target_year,
            'predictions': predictions,
            'user_profile': user_profile
        }

    def get_career_insights(self, user_profile: Dict) -> Dict:
        """
        Generate career insights based on user profile.

        Args:
            user_profile: User profile data

        Returns:
            Career insights and recommendations
        """
        # Generate short-term (5 year) scenarios
        scenarios = self.simulator.generate_scenarios(user_profile, years=5)
        comparisons = self.simulator.compare_scenarios(scenarios)

        realistic = comparisons['realistic']
        optimistic = comparisons['optimistic']

        # Calculate growth potential
        growth_potential = (
            (optimistic['final_salary'] - realistic['final_salary']) /
            realistic['final_salary'] * 100
        )

        # Determine career stage
        experience = user_profile.get('experience_years', 0)
        if experience < 3:
            career_stage = 'early'
        elif experience < 8:
            career_stage = 'mid'
        else:
            career_stage = 'senior'

        insights = {
            'career_stage': career_stage,
            'current_field': user_profile.get('field', 'unknown'),
            'growth_potential': round(growth_potential, 1),
            'expected_5yr_salary': realistic['final_salary'],
            'optimistic_5yr_salary': optimistic['final_salary'],
            'promotion_probability': realistic.get('total_promotions', 0) / 5,
            'expected_satisfaction': realistic['avg_life_satisfaction'],
            'recommendations': self._generate_recommendations(
                user_profile,
                career_stage,
                growth_potential,
                realistic
            )
        }

        return insights

    def _generate_recommendations(
        self,
        user_profile: Dict,
        career_stage: str,
        growth_potential: float,
        realistic_stats: Dict
    ) -> List[str]:
        """Generate personalized career recommendations."""
        recommendations = []

        # Stage-based recommendations
        if career_stage == 'early':
            recommendations.append("Focus on skill development and building foundational experience")
            recommendations.append("Seek mentorship opportunities to accelerate learning")
        elif career_stage == 'mid':
            recommendations.append("Consider leadership roles or specialized expertise paths")
            recommendations.append("Network actively within your industry")
        else:
            recommendations.append("Leverage your experience for senior or executive positions")
            recommendations.append("Consider mentoring others and thought leadership")

        # Growth potential recommendations
        if growth_potential > 30:
            recommendations.append("High growth potential detected - pursue aggressive career advancement")
        elif growth_potential < 15:
            recommendations.append("Consider additional certifications or field transition for higher growth")

        # Field-specific recommendations
        field = user_profile.get('field', '').lower()
        field_recs = {
            'technology': "Stay current with emerging technologies and frameworks",
            'finance': "Pursue advanced certifications (CFA, CPA) for career growth",
            'healthcare': "Specialize in high-demand areas or management roles",
            'education': "Consider administrative or curriculum development positions",
            'business': "Develop cross-functional expertise and strategic thinking skills"
        }

        if field in field_recs:
            recommendations.append(field_recs[field])

        # Satisfaction-based recommendations
        if realistic_stats['avg_life_satisfaction'] < 7:
            recommendations.append("Focus on work-life balance to improve overall satisfaction")

        return recommendations[:5]  # Return top 5 recommendations


if __name__ == "__main__":
    # Example usage
    print("=== Scenario Service Example ===\n")

    # Initialize service
    service = ScenarioService()

    # Example user profile
    user_profile = {
        'age': 28,
        'education': 'bachelors',
        'field': 'technology',
        'experience_years': 4,
        'current_salary': 85000,
        'location_type': 'urban',
        'remote_work': 'hybrid'
    }

    print("User Profile:")
    for key, value in user_profile.items():
        print(f"  {key}: {value}")
    print()

    # Generate complete scenarios
    print("Generating complete scenarios with narratives...\n")
    result = service.generate_complete_scenarios(user_profile, years=10)

    # Display results
    print("=== SCENARIO RESULTS ===\n")
    for scenario_type in ['optimistic', 'realistic', 'pessimistic']:
        scenario = result['scenarios'][scenario_type]
        stats = scenario['statistics']

        print(f"{scenario_type.upper()}:")
        print(f"  Final Salary: ${stats['final_salary']:,.2f}")
        print(f"  Salary Growth: {stats['salary_growth']:.1f}%")
        print(f"  Avg Life Satisfaction: {stats['avg_life_satisfaction']}/10")
        print(f"\nNarrative:\n{scenario['narrative']}\n")
        print("-" * 70 + "\n")

    # Display comparison
    print("=== COMPARISON SUMMARY ===")
    print(result['comparison_narrative'])
    print("\n" + "=" * 70 + "\n")

    # Get career insights
    print("=== CAREER INSIGHTS ===")
    insights = service.get_career_insights(user_profile)
    print(f"Career Stage: {insights['career_stage']}")
    print(f"Growth Potential: {insights['growth_potential']}%")
    print(f"Expected 5-Year Salary: ${insights['expected_5yr_salary']:,.2f}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f"  {i}. {rec}")
