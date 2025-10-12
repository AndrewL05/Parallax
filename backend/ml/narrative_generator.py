"""
Narrative Generator
Integrate LLM (OpenRouter) to generate natural language narratives for life scenarios.

This module wraps ML scenario predictions with human-readable narratives.
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI


class NarrativeGenerator:
    """
    Generate natural language narratives for life scenarios using LLM.

    Converts ML predictions and scenario data into engaging, personalized stories
    about potential life paths.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize narrative generator with OpenRouter API.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            base_url: OpenRouter base URL (defaults to standard URL)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or "https://openrouter.ai/api/v1"

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            print("[OK] LLM client initialized")
        else:
            self.client = None
            print("[WARN] No OpenRouter API key found, narratives will be template-based")

    def generate_scenario_narrative(
        self,
        user_profile: Dict,
        scenario_type: str,
        timeline: List[Dict],
        comparison_stats: Dict
    ) -> str:
        """
        Generate a comprehensive narrative for a life scenario.

        Args:
            user_profile: User profile data
            scenario_type: Type of scenario (optimistic, realistic, pessimistic)
            timeline: Yearly prediction data
            comparison_stats: Summary statistics from scenario comparison

        Returns:
            Natural language narrative describing the scenario
        """
        if self.client:
            return self._generate_llm_narrative(
                user_profile,
                scenario_type,
                timeline,
                comparison_stats
            )
        else:
            return self._generate_template_narrative(
                user_profile,
                scenario_type,
                timeline,
                comparison_stats
            )

    def _generate_llm_narrative(
        self,
        user_profile: Dict,
        scenario_type: str,
        timeline: List[Dict],
        comparison_stats: Dict
    ) -> str:
        """Generate narrative using LLM."""
        # Prepare context for LLM
        context = self._prepare_context(user_profile, scenario_type, timeline, comparison_stats)

        # Create prompt
        prompt = f"""You are a life coach and career advisor. Generate a compelling, personalized narrative for a {scenario_type} life scenario projection.

User Profile:
- Age: {user_profile.get('age')}
- Education: {user_profile.get('education')}
- Field: {user_profile.get('field')}
- Experience: {user_profile.get('experience_years')} years
- Current Salary: ${user_profile.get('current_salary', 'Not specified'):,}

Scenario Summary:
- Type: {scenario_type.upper()}
- Final Salary: ${comparison_stats['final_salary']:,.2f} (Growth: {comparison_stats['salary_growth']:.1f}%)
- Promotions: {comparison_stats['total_promotions']}
- Avg Life Satisfaction: {comparison_stats['avg_life_satisfaction']}/10
- Avg Career Growth: {comparison_stats['avg_career_growth_index']}/100
- Final Financial Security: {comparison_stats['final_financial_security']}/10

Key Life Events:
{self._format_life_events(timeline)}

Generate a narrative (2-3 paragraphs) that:
1. Opens with an engaging description of this potential life path
2. Highlights key career milestones and life events
3. Discusses the emotional and financial journey
4. Ends with insights about this scenario

Make it personal, realistic, and thoughtful. Use a warm, professional tone."""

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-3.2-3b-instruct:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert life coach and career advisor who creates thoughtful, personalized narratives about potential life paths."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            narrative = response.choices[0].message.content.strip()
            return narrative

        except Exception as e:
            print(f"[WARN] LLM generation failed: {e}")
            return self._generate_template_narrative(
                user_profile,
                scenario_type,
                timeline,
                comparison_stats
            )

    def _generate_template_narrative(
        self,
        user_profile: Dict,
        scenario_type: str,
        timeline: List[Dict],
        comparison_stats: Dict
    ) -> str:
        """Generate narrative using templates (fallback)."""
        age = user_profile.get('age', 25)
        field = user_profile.get('field', 'your field')
        final_age = age + len(timeline)

        # Opening based on scenario type
        openings = {
            'optimistic': f"In this optimistic trajectory, your career in {field} flourishes beyond expectations.",
            'realistic': f"This realistic projection shows a steady, balanced career path in {field}.",
            'pessimistic': f"In this conservative scenario, your career in {field} faces typical challenges but maintains stability."
        }

        opening = openings.get(scenario_type, openings['realistic'])

        # Career progression summary
        salary_start = timeline[0]['salary']
        salary_end = comparison_stats['final_salary']
        growth_pct = comparison_stats['salary_growth']

        career_summary = f"Over the next {len(timeline)} years, your salary grows from ${salary_start:,.0f} to ${salary_end:,.0f} (a {growth_pct:.1f}% increase)"

        if comparison_stats['total_promotions'] > 0:
            career_summary += f", with {comparison_stats['total_promotions']} promotion{'s' if comparison_stats['total_promotions'] > 1 else ''} along the way"

        career_summary += "."

        # Key milestones
        significant_events = []
        for year_data in timeline:
            if year_data.get('is_promoted'):
                significant_events.append(f"promotion at age {year_data['age']}")
            for event in year_data.get('life_events', []):
                if any(keyword in event.lower() for keyword in ['home', 'family', 'award', 'recognition']):
                    significant_events.append(f"{event.lower()} at age {year_data['age']}")

        milestones_text = ""
        if significant_events:
            milestones_text = f" Key milestones include {', '.join(significant_events[:3])}."

        # Life satisfaction narrative
        avg_satisfaction = comparison_stats['avg_life_satisfaction']
        satisfaction_text = ""

        if avg_satisfaction >= 8:
            satisfaction_text = "Throughout this journey, you maintain high life satisfaction, finding fulfillment in both career achievements and personal growth."
        elif avg_satisfaction >= 6:
            satisfaction_text = "This path offers moderate life satisfaction, balancing professional ambitions with personal well-being."
        else:
            satisfaction_text = "While financially stable, this scenario suggests challenges in maintaining work-life balance and overall satisfaction."

        # Financial security
        final_security = comparison_stats['final_financial_security']
        financial_text = ""

        if final_security >= 8:
            financial_text = f"By age {final_age}, you achieve strong financial security, providing peace of mind and freedom for future goals."
        elif final_security >= 6:
            financial_text = f"By age {final_age}, you reach comfortable financial stability, meeting your needs with room for savings."
        else:
            financial_text = f"Financial growth remains modest but steady, requiring careful planning for long-term goals."

        # Combine all parts
        narrative = f"{opening} {career_summary}{milestones_text}\n\n{satisfaction_text} {financial_text}"

        return narrative

    def generate_comparison_summary(
        self,
        user_profile: Dict,
        all_scenarios: Dict[str, List[Dict]],
        all_comparisons: Dict[str, Dict]
    ) -> str:
        """
        Generate a summary comparing all scenarios.

        Args:
            user_profile: User profile data
            all_scenarios: All scenario timelines
            all_comparisons: Comparison statistics for all scenarios

        Returns:
            Comparative analysis narrative
        """
        if self.client:
            return self._generate_llm_comparison(
                user_profile,
                all_scenarios,
                all_comparisons
            )
        else:
            return self._generate_template_comparison(
                user_profile,
                all_scenarios,
                all_comparisons
            )

    def _generate_llm_comparison(
        self,
        user_profile: Dict,
        all_scenarios: Dict[str, List[Dict]],
        all_comparisons: Dict[str, Dict]
    ) -> str:
        """Generate comparison narrative using LLM."""
        prompt = f"""You are a career advisor analyzing different life scenarios for a client. Compare three scenarios and provide actionable insights.

User Profile:
- Age: {user_profile.get('age')}
- Field: {user_profile.get('field')}
- Education: {user_profile.get('education')}

Scenario Comparison:

OPTIMISTIC:
- Final Salary: ${all_comparisons['optimistic']['final_salary']:,.2f}
- Life Satisfaction: {all_comparisons['optimistic']['avg_life_satisfaction']}/10
- Promotions: {all_comparisons['optimistic']['total_promotions']}

REALISTIC:
- Final Salary: ${all_comparisons['realistic']['final_salary']:,.2f}
- Life Satisfaction: {all_comparisons['realistic']['avg_life_satisfaction']}/10
- Promotions: {all_comparisons['realistic']['total_promotions']}

PESSIMISTIC:
- Final Salary: ${all_comparisons['pessimistic']['final_salary']:,.2f}
- Life Satisfaction: {all_comparisons['pessimistic']['avg_life_satisfaction']}/10
- Promotions: {all_comparisons['pessimistic']['total_promotions']}

Generate a comparison summary (2-3 paragraphs) that:
1. Highlights key differences between scenarios
2. Discusses the range of possible outcomes
3. Provides insights about what factors influence each path
4. Offers actionable recommendations

Be thoughtful, realistic, and empowering."""

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-3.2-3b-instruct:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career advisor who provides thoughtful comparative analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[WARN] LLM comparison failed: {e}")
            return self._generate_template_comparison(
                user_profile,
                all_scenarios,
                all_comparisons
            )

    def _generate_template_comparison(
        self,
        user_profile: Dict,
        all_scenarios: Dict[str, List[Dict]],
        all_comparisons: Dict[str, Dict]
    ) -> str:
        """Generate comparison narrative using templates (fallback)."""
        opt = all_comparisons['optimistic']
        real = all_comparisons['realistic']
        pess = all_comparisons['pessimistic']

        # Salary range
        salary_range = opt['final_salary'] - pess['final_salary']
        salary_text = f"The three scenarios reveal a salary range of ${salary_range:,.0f}, from ${pess['final_salary']:,.0f} in the conservative path to ${opt['final_salary']:,.0f} in the optimistic trajectory."

        # Satisfaction range
        satisfaction_diff = opt['avg_life_satisfaction'] - pess['avg_life_satisfaction']
        satisfaction_text = f"Life satisfaction varies by {satisfaction_diff:.1f} points across scenarios, suggesting that career outcomes significantly impact overall well-being."

        # Realistic scenario positioning
        realistic_text = f"The realistic scenario, with a final salary of ${real['final_salary']:,.0f} and {real['avg_life_satisfaction']:.1f}/10 life satisfaction, represents a balanced middle ground that accounts for typical career progression patterns."

        # Key factors
        factors_text = "Key factors that differentiate these paths include promotion timing, skill development opportunities, and work-life balance choices. The optimistic path assumes proactive career management and favorable market conditions, while the pessimistic scenario accounts for industry challenges and slower advancement."

        # Recommendations
        recommendations_text = "To trend toward the optimistic scenario, focus on continuous learning, networking, and strategic career moves. However, the realistic path offers a dependable foundation with less pressure and more predictable outcomes."

        comparison = f"{salary_text} {satisfaction_text}\n\n{realistic_text} {factors_text}\n\n{recommendations_text}"

        return comparison

    def _prepare_context(
        self,
        user_profile: Dict,
        scenario_type: str,
        timeline: List[Dict],
        comparison_stats: Dict
    ) -> Dict:
        """Prepare structured context for LLM."""
        return {
            'user_profile': user_profile,
            'scenario_type': scenario_type,
            'timeline_length': len(timeline),
            'first_year': timeline[0] if timeline else {},
            'last_year': timeline[-1] if timeline else {},
            'stats': comparison_stats
        }

    def _format_life_events(self, timeline: List[Dict]) -> str:
        """Format life events for prompt."""
        all_events = []
        for year_data in timeline:
            events = year_data.get('life_events', [])
            if events:
                age = year_data.get('age')
                for event in events:
                    all_events.append(f"- Age {age}: {event}")

        return "\n".join(all_events[:10]) if all_events else "- Steady career progression"

    def generate_year_narrative(self, year_data: Dict) -> str:
        """
        Generate a brief narrative for a single year.

        Args:
            year_data: Data for a single year from timeline

        Returns:
            Short narrative for that year
        """
        age = year_data.get('age')
        salary = year_data.get('salary', 0)
        satisfaction = year_data.get('life_satisfaction', 0)
        events = year_data.get('life_events', [])
        is_promoted = year_data.get('is_promoted', False)

        # Build narrative
        parts = []

        if is_promoted:
            parts.append(f"At age {age}, you receive a promotion, bringing your salary to ${salary:,.0f}.")
        else:
            parts.append(f"At age {age}, you earn ${salary:,.0f}.")

        if events:
            parts.append(f" {events[0]}.")

        # Add satisfaction context
        if satisfaction >= 8:
            parts.append(" You feel fulfilled and optimistic about the future.")
        elif satisfaction >= 6:
            parts.append(" Life feels balanced and stable.")
        else:
            parts.append(" You face some challenges but remain resilient.")

        return " ".join(parts)


if __name__ == "__main__":
    # Example usage
    print("=== Narrative Generator Example ===\n")

    # Initialize generator
    generator = NarrativeGenerator()

    # Example scenario data
    user_profile = {
        'age': 28,
        'education': 'bachelors',
        'field': 'technology',
        'experience_years': 4,
        'current_salary': 85000
    }

    comparison_stats = {
        'final_salary': 140693.54,
        'salary_growth': 59.5,
        'total_promotions': 1,
        'avg_life_satisfaction': 8.06,
        'avg_career_growth_index': 39.06,
        'final_financial_security': 7.82
    }

    timeline = [
        {
            'year': 1,
            'age': 28,
            'salary': 85000,
            'life_satisfaction': 7.5,
            'is_promoted': False,
            'life_events': ['Started new role']
        },
        {
            'year': 5,
            'age': 32,
            'salary': 104349,
            'life_satisfaction': 8.14,
            'is_promoted': False,
            'life_events': ['Purchased first home']
        },
        {
            'year': 10,
            'age': 37,
            'salary': 140693,
            'life_satisfaction': 8.5,
            'is_promoted': True,
            'life_events': ['Received promotion to higher position']
        }
    ]

    # Generate narrative
    print("Generating realistic scenario narrative...\n")
    narrative = generator.generate_scenario_narrative(
        user_profile,
        'realistic',
        timeline,
        comparison_stats
    )

    print("=== REALISTIC SCENARIO NARRATIVE ===")
    print(narrative)
    print("\n" + "="*50 + "\n")

    # Generate year narrative
    print("Year 5 Narrative:")
    year_narrative = generator.generate_year_narrative(timeline[1])
    print(year_narrative)
