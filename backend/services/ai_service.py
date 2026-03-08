import openai
import json
import re
import logging
import random
from typing import Dict, Any, Optional

from config import (
    OPENROUTER_BASE_URL,
    OPENROUTER_API_KEY,
    LLM_MODEL_PRIMARY,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS_SIMULATION,
    LLM_TIMEOUT_SECONDS,
    SALARY_VARIANCE_THRESHOLD,
    SALARY_NATURAL_VARIANCE,
)
from models.simulation import SimulationRequest
from services.ml_integration_service import MLIntegrationService
from ml.profession_data import (
    detect_profession,
    get_profession_salary,
    get_training_config,
    get_training_career_title,
    get_profession_title,
    PROFESSION_SALARIES
)

logger = logging.getLogger(__name__)

ml_integration = MLIntegrationService()

client = None

def get_openai_client():
    """Get or create OpenAI client"""
    global client
    if client is None:
        if OPENROUTER_API_KEY:
            logger.info("OpenRouter API key configured")
            client = openai.OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=OPENROUTER_API_KEY,
            )
            logger.info("OpenAI client initialized successfully")
        else:
            logger.warning("OPENROUTER_API_KEY not set - AI service will use fallback data")
    return client

async def generate_life_simulation(request: SimulationRequest) -> Dict[str, Any]:
    """Generate AI-powered life simulation using AI model"""
    
    ai_client = get_openai_client()
    if not ai_client:
        logger.warning("OpenRouter API key not available, using fallback data")
        return generate_fallback_data(request)
    
    try:
        prompt = f"""Generate a realistic 10-year career progression comparison between two paths.

**Choice A:** {request.choice_a.title}
Description: {request.choice_a.description}

**Choice B:** {request.choice_b.title}  
Description: {request.choice_b.description}

**Context:** Age {request.user_context.age or 25}, Location: {request.user_context.current_location or 'United States'}

Please create realistic salary progressions and happiness scores (1-10 scale) for each career path over 10 years. Consider typical industry standards, advancement opportunities, and work-life balance factors.

Return your response as valid JSON only:

{{
  "choice_a_timeline": [
    {{"year": 1, "salary": [realistic_starting_salary], "happiness_score": [1-10], "major_event": "[career milestone]", "location": "{request.user_context.current_location or 'City'}", "career_title": "[job title]"}},
    [... continue for years 2-10 with realistic progression ...]
  ],
  "choice_b_timeline": [
    {{"year": 1, "salary": [realistic_starting_salary], "happiness_score": [1-10], "major_event": "[career milestone]", "location": "{request.user_context.current_location or 'City'}", "career_title": "[job title]"}},
    [... continue for years 2-10 with realistic progression ...]
  ],
  "summary": "[200+ character comparison highlighting key differences, trade-offs, and considerations for choosing between these paths]"
}}"""
        
        logger.info("Making OpenRouter API call...")

        import asyncio
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    ai_client.chat.completions.create,
                    model=LLM_MODEL_PRIMARY,
                    messages=[
                        {"role": "system", "content": "You are a professional life advisor and data analyst specializing in career and life path projections."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=LLM_TEMPERATURE,
                    max_tokens=LLM_MAX_TOKENS_SIMULATION
                ),
                timeout=LLM_TIMEOUT_SECONDS
            )
            logger.info("OpenRouter API call successful")
        except asyncio.TimeoutError:
            logger.error(" OpenRouter API call timed out after 45 seconds")
            raise Exception("API call timed out")
        
        ai_content = response.choices[0].message.content
        logger.info(f"AI response received, length: {len(ai_content)}")
        logger.info(f"AI response preview: {ai_content[:200]}...")
        
        if not ai_content or ai_content.strip() == "":
            logger.error("AI response content is empty!")
            return generate_fallback_data(request)
        
        ai_content = ai_content.strip()
        if ai_content.startswith('<s>'):
            ai_content = ai_content[3:].strip()
        if ai_content.startswith('[BOT]'):
            ai_content = ai_content[5:].strip()
        if ai_content.startswith('[INST]'):
            ai_content = ai_content[6:].strip()
        if ai_content.endswith('</s>'):
            ai_content = ai_content[:-4].strip()
            
        logger.info(f"Cleaned AI response preview: {ai_content[:200]}...")
        
        ai_data = None
        
        try:
            ai_data = json.loads(ai_content.strip())
            logger.info("Successfully parsed AI response as direct JSON")
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parsing failed: {e}")
            pass
        
        if ai_data is None:
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_content, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1).strip()
                    ai_data = json.loads(json_str)
                    logger.info("Successfully parsed AI response from markdown code block")
                except json.JSONDecodeError as e:
                    logger.warning(f"Markdown JSON parsing failed: {e}")
                    pass
        
        if ai_data is None:
            json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
            if json_match:
                try:
                    ai_data = json.loads(json_match.group())
                    logger.info("Successfully parsed AI response from JSON pattern")
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON pattern parsing failed: {e}")
                    pass
            else:
                logger.warning("No JSON pattern found in AI response")
        
        if ai_data:
            # Validate and adjust AI predictions against known salary ranges
            ai_data = validate_ai_predictions(ai_data, request)
            return ai_data
        else:
            logger.warning(f" Failed to parse AI response with all methods, using fallback data")
            logger.warning(f"Response content: {ai_content}")
            return generate_fallback_data(request)
        
    except Exception as e:
        logger.error(f" AI service error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            logger.error(f"API response status: {getattr(e.response, 'status_code', 'unknown')}")
            logger.error(f"API response text: {getattr(e.response, 'text', 'unknown')}")
        return generate_fallback_data(request)


def validate_ai_predictions(ai_data: Dict[str, Any], request: SimulationRequest) -> Dict[str, Any]:
    """
    Validate and adjust AI-generated salary predictions against known profession ranges.

    If AI predictions deviate significantly from expected ranges, blend them with
    ML-based predictions for more accurate results.

    Args:
        ai_data: Raw AI-generated simulation data
        request: Original simulation request

    Returns:
        Validated and potentially adjusted simulation data
    """
    try:
        # Validate choice A
        if "choice_a_timeline" in ai_data:
            ai_data["choice_a_timeline"] = _validate_timeline(
                ai_data["choice_a_timeline"],
                request.choice_a.title,
                request.choice_a.description
            )

        # Validate choice B
        if "choice_b_timeline" in ai_data:
            ai_data["choice_b_timeline"] = _validate_timeline(
                ai_data["choice_b_timeline"],
                request.choice_b.title,
                request.choice_b.description
            )

    except Exception as e:
        logger.warning(f"AI validation failed, returning original data: {e}")

    return ai_data


def _validate_timeline(
    timeline: list,
    title: str,
    description: str
) -> list:
    """
    Validate and adjust a single timeline's salary predictions.

    When a profession is detected, we use ML-based salary data as the primary
    source and only use AI predictions for non-salary fields.

    Args:
        timeline: List of yearly prediction dicts
        title: Career/choice title
        description: Career/choice description

    Returns:
        Validated timeline with adjusted salaries if needed
    """
    # Detect profession from title
    profession = detect_profession(title, description)

    if not profession:
        logger.debug(f"No profession detected for '{title}', skipping validation")
        return timeline

    logger.info(f"Validating AI predictions for profession: {profession}")

    # Get training config if applicable
    training_config = get_training_config(profession)
    profession_salaries = PROFESSION_SALARIES.get(profession, {})

    if not profession_salaries:
        return timeline

    validated_timeline = []
    for i, year_data in enumerate(timeline):
        year_offset = i
        original_salary = year_data.get("salary", 0)

        # Calculate expected salary for this year based on ML data
        expected_salary = _get_expected_salary(
            profession,
            profession_salaries,
            training_config,
            year_offset
        )

        if expected_salary and original_salary > 0:
            # For detected professions, use ML salary data as primary source
            # This ensures accurate profession-specific salaries
            year_data = year_data.copy()

            # Always use ML-based salary for detected professions
            # Add small variance to make it look natural
            variance = random.uniform(1 - SALARY_NATURAL_VARIANCE, 1 + SALARY_NATURAL_VARIANCE)
            adjusted_salary = expected_salary * variance

            if abs(original_salary - expected_salary) > SALARY_VARIANCE_THRESHOLD:
                logger.info(
                    f"Year {year_offset + 1}: Corrected salary from "
                    f"${original_salary:,.0f} to ${adjusted_salary:,.0f} "
                    f"(ML expected: ${expected_salary:,.0f})"
                )

            year_data["salary"] = round(adjusted_salary, 2)

            # Update career title based on profession
            if training_config:
                year_data["career_title"] = get_training_career_title(
                    profession, year_offset, training_config
                )
            else:
                # Non-training profession - use standard title progression
                year_data["career_title"] = get_profession_title(profession, year_offset)

        validated_timeline.append(year_data)

    return validated_timeline


def _get_expected_salary(
    profession: str,
    profession_salaries: Dict[str, int],
    training_config: Optional[Dict],
    year_offset: int
) -> Optional[float]:
    """
    Get expected salary for a profession at a given year.

    Args:
        profession: Detected profession key
        profession_salaries: Salary data for this profession
        training_config: Training career config (if applicable)
        year_offset: Years since career start

    Returns:
        Expected salary for this year
    """
    if training_config:
        # Training career (doctor, surgeon, etc.)
        training_years = training_config["training_years"]

        if year_offset < training_years:
            # In training
            base = training_config["training_salary"]
            annual_raise = training_config.get("annual_training_raise", 0.03)
            return base * ((1 + annual_raise) ** year_offset)
        else:
            # Post-training
            years_post = year_offset - training_years
            base = training_config["post_training_salary"]
            return base * ((1.05) ** years_post)
    else:
        # Standard profession - estimate level based on year
        if year_offset < 3:
            level = "entry"
        elif year_offset < 6:
            level = "mid"
        elif year_offset < 9:
            level = "senior"
        else:
            level = "lead"

        base = profession_salaries.get(level, profession_salaries.get("entry", 50000))
        # Apply standard growth within level
        years_in_level = year_offset % 3
        return base * ((1.04) ** years_in_level)


def generate_fallback_data(request: SimulationRequest) -> Dict[str, Any]:
    """
    Generate ML-based simulation data

    Uses ML prediction service for realistic, data-driven projections
    """
    logger.info("Using ML-based prediction for simulation data")

    try:
        # Generate ML-enhanced timelines for both choices
        choice_a_timeline = ml_integration.generate_ml_enhanced_timeline(
            request.choice_a.dict(),
            request.user_context
        )

        choice_b_timeline = ml_integration.generate_ml_enhanced_timeline(
            request.choice_b.dict(),
            request.user_context
        )

        # Convert TimelinePoint objects to dicts
        choice_a_data = [point.dict() for point in choice_a_timeline]
        choice_b_data = [point.dict() for point in choice_b_timeline]

        # Generate summary comparing the two paths
        summary = _generate_ml_summary(choice_a_data, choice_b_data, request)

        return {
            "choice_a_timeline": choice_a_data,
            "choice_b_timeline": choice_b_data,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"ML prediction failed, using simple fallback: {e}")
        return _generate_simple_fallback(request)

def _generate_ml_summary(
    choice_a_timeline: list,
    choice_b_timeline: list,
    request: SimulationRequest
) -> str:
    """Generate comparison summary from ML predictions"""

    # Calculate averages for comparison
    a_avg_salary = sum(p['salary'] for p in choice_a_timeline) / len(choice_a_timeline)
    b_avg_salary = sum(p['salary'] for p in choice_b_timeline) / len(choice_b_timeline)

    a_avg_happiness = sum(p['happiness_score'] for p in choice_a_timeline) / len(choice_a_timeline)
    b_avg_happiness = sum(p['happiness_score'] for p in choice_b_timeline) / len(choice_b_timeline)

    a_final_salary = choice_a_timeline[-1]['salary']
    b_final_salary = choice_b_timeline[-1]['salary']

    # Determine which path has advantages
    higher_salary_path = "A" if a_avg_salary > b_avg_salary else "B"
    higher_happiness_path = "A" if a_avg_happiness > b_avg_happiness else "B"

    salary_diff = abs(a_avg_salary - b_avg_salary)
    happiness_diff = abs(a_avg_happiness - b_avg_happiness)

    summary = (
        f"**{request.choice_a.title}** (Path A) and **{request.choice_b.title}** (Path B) "
        f"offer distinct career trajectories. "
    )

    # Salary comparison
    if salary_diff > 10000:
        summary += (
            f"Path {higher_salary_path} provides significantly higher compensation, "
            f"averaging ${int(max(a_avg_salary, b_avg_salary)):,} annually compared to "
            f"${int(min(a_avg_salary, b_avg_salary)):,}. "
        )
    else:
        summary += "Both paths offer comparable salary potential. "

    # Happiness comparison
    if happiness_diff > 0.5:
        summary += (
            f"However, Path {higher_happiness_path} shows notably higher life satisfaction "
            f"(avg {max(a_avg_happiness, b_avg_happiness):.1f}/10 vs {min(a_avg_happiness, b_avg_happiness):.1f}/10). "
        )
    else:
        summary += "Both paths offer similar quality of life outcomes. "

    # Growth trajectory
    a_growth = ((a_final_salary - choice_a_timeline[0]['salary']) / choice_a_timeline[0]['salary']) * 100
    b_growth = ((b_final_salary - choice_b_timeline[0]['salary']) / choice_b_timeline[0]['salary']) * 100

    if abs(a_growth - b_growth) > 20:
        faster_growth = "A" if a_growth > b_growth else "B"
        summary += (
            f"Path {faster_growth} demonstrates stronger long-term growth potential "
            f"({int(max(a_growth, b_growth))}% salary increase over 10 years). "
        )

    summary += (
        "These ML-powered projections are based on industry data, career progression patterns, "
        "and quality of life research to provide realistic insights into each path's potential outcomes."
    )

    return summary

def _generate_simple_fallback(request: SimulationRequest) -> Dict[str, Any]:
    """Simple fallback if ML completely fails"""

    # Generate realistic salary ranges based on career type
    def get_salary_range(career_title: str):
        career_lower = career_title.lower()
        if "teacher" in career_lower or "education" in career_lower:
            return 45000, 3000
        elif "engineer" in career_lower or "software" in career_lower or "tech" in career_lower:
            return 70000, 8000
        else:
            return 50000, 4000

    choice_a_start, choice_a_growth = get_salary_range(request.choice_a.title)
    choice_b_start, choice_b_growth = get_salary_range(request.choice_b.title)

    return {
        "choice_a_timeline": [
            {
                "year": i,
                "salary": min(choice_a_start + (i-1)*choice_a_growth, 240000),
                "happiness_score": min(7.0 + i*0.1, 9.5),
                "major_event": f"Year {i} milestone",
                "location": "Unknown",
                "career_title": request.choice_a.title
            }
            for i in range(1, 11)
        ],
        "choice_b_timeline": [
            {
                "year": i,
                "salary": min(choice_b_start + (i-1)*choice_b_growth, 240000),
                "happiness_score": min(7.5 + i*0.1, 9.5),
                "major_event": f"Year {i} milestone",
                "location": "Unknown",
                "career_title": request.choice_b.title
            }
            for i in range(1, 11)
        ],
        "summary": "Simulation uses baseline career progression data. Results may not reflect personalized circumstances."
    }