"""
Scenario Simulator
Generate realistic future life scenarios using ML models and enhanced features.

This module creates multiple scenario variations (optimistic, realistic, pessimistic)
based on user input and trained ML models.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib
from datetime import datetime, timedelta


class ScenarioSimulator:
    """
    Generate future life scenarios with multiple variations.

    Uses trained ML models and enhanced features to project:
    - Salary trajectories with variations
    - Career growth paths
    - Life satisfaction over time
    - Major life events and milestones
    """

    def __init__(self, models_dir: str = "models", features_dir: str = "data/features"):
        """
        Initialize scenario simulator with trained models.

        Args:
            models_dir: Directory containing trained model files
            features_dir: Directory containing feature engineering data
        """
        self.models_dir = Path(models_dir)
        self.features_dir = Path(features_dir)
        self.model = None
        self.feature_stats = None

        self._load_models()
        self._load_feature_stats()

    def _load_models(self):
        """Load trained ML models."""
        try:
            model_path = self.models_dir / "xgboost_tuned_salary.pkl"
            if model_path.exists():
                self.model = joblib.load(model_path)
                print(f"[OK] Loaded model: {model_path.name}")
            else:
                print(f"[WARN] Model not found: {model_path}")
        except Exception as e:
            print(f"[WARN] Error loading model: {e}")

    def _load_feature_stats(self):
        """Load feature statistics for realistic bounds."""
        try:
            features_path = self.features_dir / "salary_features_enhanced.csv"
            if features_path.exists():
                df = pd.read_csv(features_path)
                self.feature_stats = {
                    'salary': {
                        'mean': df[[col for col in df.columns if 'salary' in col.lower() and 'category' not in col.lower()]][0].mean() if any('salary' in col.lower() for col in df.columns) else 100000,
                        'std': df[[col for col in df.columns if 'salary' in col.lower() and 'category' not in col.lower()]][0].std() if any('salary' in col.lower() for col in df.columns) else 30000,
                        'min': df[[col for col in df.columns if 'salary' in col.lower() and 'category' not in col.lower()]][0].min() if any('salary' in col.lower() for col in df.columns) else 30000,
                        'max': df[[col for col in df.columns if 'salary' in col.lower() and 'category' not in col.lower()]][0].max() if any('salary' in col.lower() for col in df.columns) else 400000,
                    },
                    'career_growth_index': {
                        'mean': df['career_growth_index'].mean() if 'career_growth_index' in df.columns else 62.9,
                        'std': df['career_growth_index'].std() if 'career_growth_index' in df.columns else 15.0,
                    },
                    'life_satisfaction_composite': {
                        'mean': df['life_satisfaction_composite'].mean() if 'life_satisfaction_composite' in df.columns else 5.47,
                        'std': df['life_satisfaction_composite'].std() if 'life_satisfaction_composite' in df.columns else 1.2,
                    }
                }
                print(f"[OK] Loaded feature statistics from enhanced dataset")
        except Exception as e:
            print(f"[WARN] Error loading feature stats: {e}")
            self.feature_stats = {
                'salary': {'mean': 100000, 'std': 30000, 'min': 30000, 'max': 400000},
                'career_growth_index': {'mean': 62.9, 'std': 15.0},
                'life_satisfaction_composite': {'mean': 5.47, 'std': 1.2}
            }

    def generate_scenarios(
        self,
        user_profile: Dict,
        years: int = 10,
        num_variations: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Generate multiple scenario variations for a user profile.

        Args:
            user_profile: User information including:
                - age: Current age
                - education: Education level (high_school, bachelors, masters, phd)
                - field: Career field (technology, finance, healthcare, etc.)
                - experience_years: Years of professional experience
                - current_salary: Current salary (optional)
                - location_type: Location (urban, suburban, rural)
                - remote_work: Remote work status (full, hybrid, none)
            years: Number of years to project (default 10)
            num_variations: Number of scenario variations (default 3: optimistic, realistic, pessimistic)

        Returns:
            Dictionary with scenario variations:
            {
                'optimistic': [yearly_data],
                'realistic': [yearly_data],
                'pessimistic': [yearly_data]
            }
        """
        scenarios = {}

        variations = {
            'optimistic': {'growth': 1.3, 'stability': 1.2, 'satisfaction': 1.15, 'events': 'positive'},
            'realistic': {'growth': 1.0, 'stability': 1.0, 'satisfaction': 1.0, 'events': 'mixed'},
            'pessimistic': {'growth': 0.7, 'stability': 0.85, 'satisfaction': 0.9, 'events': 'negative'}
        }

        for scenario_name, multipliers in variations.items():
            scenarios[scenario_name] = self._generate_timeline(
                user_profile,
                years,
                multipliers
            )

        return scenarios

    def _generate_timeline(
        self,
        user_profile: Dict,
        years: int,
        multipliers: Dict
    ) -> List[Dict]:
        """
        Generate a single timeline scenario.

        Args:
            user_profile: User profile data
            years: Number of years to project
            multipliers: Scenario variation multipliers

        Returns:
            List of yearly predictions with all metrics
        """
        timeline = []
        current_age = user_profile.get('age', 25)
        current_experience = user_profile.get('experience_years', 0)
        field = user_profile.get('field', 'business')
        education = user_profile.get('education', 'bachelors')

        current_salary = user_profile.get('current_salary') or self._estimate_base_salary(
            field, education, current_experience
        )

        career_state = {
            'salary': current_salary,
            'position_level': self._infer_position_level(current_experience, current_salary),
            'years_in_position': 0,
            'total_experience': current_experience,
            'field': field,
            'education': education,
            'stability_score': 0.8,
            'satisfaction_score': 7.0
        }

        for year in range(years):
            year_data = self._simulate_year(
                career_state,
                current_age + year,
                multipliers,
                year
            )
            timeline.append(year_data)

            self._update_career_state(career_state, year_data, multipliers)

        return timeline

    def _simulate_year(
        self,
        career_state: Dict,
        age: int,
        multipliers: Dict,
        year_index: int
    ) -> Dict:
        """
        Simulate a single year with all metrics and events.

        Args:
            career_state: Current career state
            age: Current age
            multipliers: Scenario variation multipliers
            year_index: Year number (0-based)

        Returns:
            Dictionary with all yearly metrics
        """
        base_growth_rate = self._calculate_growth_rate(career_state, multipliers)

        new_salary = career_state['salary'] * (1 + base_growth_rate)

        promotion_prob = self._calculate_promotion_probability(career_state, year_index)
        is_promoted = np.random.random() < (promotion_prob * multipliers['growth'])

        if is_promoted:
            new_salary *= 1.15  
            career_state['position_level'] = min(career_state['position_level'] + 1, 5)
            career_state['years_in_position'] = 0

        career_growth_index = self._calculate_career_growth_index(career_state, new_salary)

        life_satisfaction = self._calculate_life_satisfaction(
            career_state,
            new_salary,
            age,
            multipliers
        )

        financial_security = self._calculate_financial_security(new_salary, age)

        work_life_balance = self._calculate_work_life_balance(
            career_state['position_level'],
            career_state['field']
        )

        life_events = self._generate_life_events(
            age,
            year_index,
            multipliers['events'],
            is_promoted
        )

        return {
            'year': year_index + 1,
            'age': age,
            'salary': round(new_salary, 2),
            'position_level': career_state['position_level'],
            'career_growth_index': round(career_growth_index, 2),
            'life_satisfaction': round(life_satisfaction, 2),
            'financial_security': round(financial_security, 2),
            'work_life_balance': round(work_life_balance, 2),
            'stability_score': round(career_state['stability_score'] * 100, 2),
            'is_promoted': is_promoted,
            'life_events': life_events,
            'happiness_score': round(life_satisfaction * 1.2, 2),  # Scale to 0-10
            'stress_level': round((10 - work_life_balance) * 0.8, 2),
            'health_score': round(self._calculate_health_score(age, work_life_balance), 2)
        }

    def _estimate_base_salary(self, field: str, education: str, experience: int) -> float:
        """Estimate base salary based on field, education, and experience."""
        field_base = {
            'technology': 75000,
            'finance': 70000,
            'healthcare': 65000,
            'engineering': 70000,
            'education': 45000,
            'business': 60000,
            'creative': 50000,
            'service': 35000,
            'other': 50000
        }

        education_mult = {
            'high_school': 0.7,
            'associates': 0.85,
            'bachelors': 1.0,
            'masters': 1.25,
            'phd': 1.4
        }

        base = field_base.get(field.lower(), 50000)
        edu_mult = education_mult.get(education.lower(), 1.0)

        exp_mult = 1 + min(experience * 0.03, 0.6)

        return base * edu_mult * exp_mult

    def _infer_position_level(self, experience: int, salary: float) -> int:
        """
        Infer position level (1-5) based on experience and salary.
        1: Entry, 2: Junior, 3: Mid, 4: Senior, 5: Lead/Executive
        """
        if experience < 2:
            return 1
        elif experience < 5:
            return 2
        elif experience < 10:
            return 3
        elif experience < 15:
            return 4
        else:
            return 5

    def _calculate_growth_rate(self, career_state: Dict, multipliers: Dict) -> float:
        """Calculate annual salary growth rate."""
        base_rates = {
            1: 0.06,  # Entry: 6%
            2: 0.05,  # Junior: 5%
            3: 0.04,  # Mid: 4%
            4: 0.03,  # Senior: 3%
            5: 0.025  # Lead: 2.5%
        }

        base_rate = base_rates.get(career_state['position_level'], 0.04)

        adjusted_rate = base_rate * career_state['stability_score'] * multipliers['growth']

        random_factor = np.random.uniform(-0.01, 0.02)

        return max(0, adjusted_rate + random_factor)

    def _calculate_promotion_probability(self, career_state: Dict, year_index: int) -> float:
        """Calculate probability of promotion this year."""
        if career_state['years_in_position'] < 2:
            base_prob = 0.05
        elif career_state['years_in_position'] < 4:
            base_prob = 0.20
        else:
            base_prob = 0.35

        level_factor = {1: 1.0, 2: 0.9, 3: 0.7, 4: 0.5, 5: 0.2}
        base_prob *= level_factor.get(career_state['position_level'], 0.5)

        performance_factor = career_state['satisfaction_score'] / 7.0

        return min(base_prob * performance_factor, 0.5)

    def _calculate_career_growth_index(self, career_state: Dict, new_salary: float) -> float:
        """Calculate career growth index (0-100)."""
        salary_stats = self.feature_stats['salary']
        salary_percentile = min((new_salary - salary_stats['min']) / (salary_stats['max'] - salary_stats['min']) * 40, 40)

        experience_points = min(career_state['total_experience'] * 1.5, 30)

        position_points = career_state['position_level'] * 4

        stability_points = career_state['stability_score'] * 10

        return min(salary_percentile + experience_points + position_points + stability_points, 100)

    def _calculate_life_satisfaction(
        self,
        career_state: Dict,
        salary: float,
        age: int,
        multipliers: Dict
    ) -> float:
        """Calculate life satisfaction score (0-10)."""
        salary_stats = self.feature_stats['salary']
        financial_score = min((salary / salary_stats['mean']) * 1.75, 3.5)

        career_score = career_state['satisfaction_score'] / 7.0 * 2.5

        wlb_score = self._calculate_work_life_balance(
            career_state['position_level'],
            career_state['field']
        ) / 10 * 2

        stability_score = career_state['stability_score'] * 2

        base_satisfaction = financial_score + career_score + wlb_score + stability_score

        age_factor = 1.0 if age < 30 else 1.1 if age < 50 else 0.95

        return min(base_satisfaction * multipliers['satisfaction'] * age_factor, 10)

    def _calculate_financial_security(self, salary: float, age: int) -> float:
        """Calculate financial security score (0-10)."""
        expected_salary = {
            25: 50000, 30: 70000, 35: 90000, 40: 110000,
            45: 120000, 50: 130000, 55: 135000, 60: 140000
        }

        nearest_age = min(expected_salary.keys(), key=lambda x: abs(x - age))
        expected = expected_salary[nearest_age]

        ratio = salary / expected
        return min(ratio * 5, 10)

    def _calculate_work_life_balance(self, position_level: int, field: str) -> float:
        """Calculate work-life balance score (0-10)."""
        level_impact = {1: 8.5, 2: 8.0, 3: 7.0, 4: 6.0, 5: 5.5}
        base_score = level_impact.get(position_level, 7.0)

        field_adjustments = {
            'technology': -0.5,
            'finance': -1.0,
            'healthcare': -0.8,
            'engineering': -0.3,
            'education': 0.5,
            'business': -0.5,
            'creative': 0.3,
            'service': 0.0
        }

        adjustment = field_adjustments.get(field.lower(), 0)

        return max(min(base_score + adjustment + np.random.uniform(-0.5, 0.5), 10), 3)

    def _calculate_health_score(self, age: int, work_life_balance: float) -> float:
        """Calculate health score (0-10) based on age and lifestyle."""
        if age < 30:
            base_health = 9.0
        elif age < 40:
            base_health = 8.5
        elif age < 50:
            base_health = 8.0
        elif age < 60:
            base_health = 7.5
        else:
            base_health = 7.0

        wlb_impact = (work_life_balance - 5) * 0.2

        return max(min(base_health + wlb_impact + np.random.uniform(-0.3, 0.3), 10), 4)

    def _generate_life_events(
        self,
        age: int,
        year_index: int,
        event_tone: str,
        is_promoted: bool
    ) -> List[str]:
        """Generate realistic life events for the year."""
        events = []

        if is_promoted:
            events.append("Received promotion to higher position")

        if age == 30 and year_index < 3:
            events.append("Considering major life decisions")

        if 28 <= age <= 35 and np.random.random() < 0.15:
            events.append("Purchased first home" if event_tone != 'negative' else "Dealing with housing market challenges")

        if 25 <= age <= 40 and np.random.random() < 0.1:
            events.append("Started family" if event_tone == 'optimistic' else "Considering family planning")

        if year_index > 2 and np.random.random() < 0.12:
            if event_tone == 'optimistic':
                events.append("Received recognition award or bonus")
            elif event_tone == 'negative':
                events.append("Faced workplace challenges")
            else:
                events.append("Completed professional development course")

        if np.random.random() < 0.08:
            if event_tone == 'optimistic':
                positive_events = [
                    "Started successful side project",
                    "Made valuable professional connections",
                    "Achieved personal milestone",
                    "Improved health and fitness"
                ]
                events.append(np.random.choice(positive_events))
            elif event_tone == 'negative':
                negative_events = [
                    "Dealt with unexpected expenses",
                    "Faced industry challenges",
                    "Navigated organizational changes"
                ]
                events.append(np.random.choice(negative_events))

        return events if events else ["Steady progress in career and life"]

    def _update_career_state(self, career_state: Dict, year_data: Dict, multipliers: Dict):
        """Update career state based on year results."""
        career_state['salary'] = year_data['salary']
        career_state['position_level'] = year_data['position_level']
        career_state['years_in_position'] += 1 if not year_data['is_promoted'] else 0
        career_state['total_experience'] += 1

        stability_change = np.random.uniform(-0.05, 0.05) * multipliers['stability']
        career_state['stability_score'] = max(min(career_state['stability_score'] + stability_change, 1.0), 0.6)

        satisfaction_change = 0.1 if year_data['is_promoted'] else np.random.uniform(-0.2, 0.2)
        career_state['satisfaction_score'] = max(min(career_state['satisfaction_score'] + satisfaction_change, 10), 4)

    def compare_scenarios(self, scenarios: Dict[str, List[Dict]]) -> Dict:
        """
        Compare different scenarios and provide summary statistics.

        Args:
            scenarios: Output from generate_scenarios()

        Returns:
            Comparison statistics across scenarios
        """
        comparison = {}

        for scenario_name, timeline in scenarios.items():
            final_year = timeline[-1]

            # Calculate averages
            avg_satisfaction = np.mean([year['life_satisfaction'] for year in timeline])
            avg_growth_index = np.mean([year['career_growth_index'] for year in timeline])
            total_promotions = sum([1 for year in timeline if year['is_promoted']])

            comparison[scenario_name] = {
                'final_salary': final_year['salary'],
                'salary_growth': ((final_year['salary'] - timeline[0]['salary']) / timeline[0]['salary']) * 100,
                'final_position_level': final_year['position_level'],
                'avg_life_satisfaction': round(avg_satisfaction, 2),
                'avg_career_growth_index': round(avg_growth_index, 2),
                'total_promotions': total_promotions,
                'final_financial_security': final_year['financial_security'],
                'avg_work_life_balance': round(np.mean([year['work_life_balance'] for year in timeline]), 2),
                'total_life_events': sum([len(year['life_events']) for year in timeline])
            }

        return comparison


if __name__ == "__main__":
    print("=== Scenario Simulator Example ===\n")

    simulator = ScenarioSimulator()

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

    print("Generating 10-year scenarios...")
    scenarios = simulator.generate_scenarios(user_profile, years=10)

    print("\n=== Scenario Comparison ===\n")
    comparison = simulator.compare_scenarios(scenarios)

    for scenario_name, stats in comparison.items():
        print(f"{scenario_name.upper()} SCENARIO:")
        print(f"  Final Salary: ${stats['final_salary']:,.2f} (+{stats['salary_growth']:.1f}%)")
        print(f"  Total Promotions: {stats['total_promotions']}")
        print(f"  Avg Life Satisfaction: {stats['avg_life_satisfaction']}/10")
        print(f"  Avg Career Growth Index: {stats['avg_career_growth_index']}/100")
        print(f"  Final Financial Security: {stats['final_financial_security']}/10")
        print(f"  Avg Work-Life Balance: {stats['avg_work_life_balance']}/10")
        print()

    print("=== Sample Year (Realistic Scenario, Year 5) ===")
    year_5 = scenarios['realistic'][4]
    print(f"Age: {year_5['age']}")
    print(f"Salary: ${year_5['salary']:,.2f}")
    print(f"Position Level: {year_5['position_level']}/5")
    print(f"Career Growth Index: {year_5['career_growth_index']}/100")
    print(f"Life Satisfaction: {year_5['life_satisfaction']}/10")
    print(f"Promoted: {'Yes' if year_5['is_promoted'] else 'No'}")
    print(f"Life Events: {', '.join(year_5['life_events'])}")
