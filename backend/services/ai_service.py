import openai
import json
import re
import logging
import os
from typing import Dict, Any

from models.simulation import SimulationRequest
from services.ml_integration_service import MLIntegrationService

logger = logging.getLogger(__name__)

ml_integration = MLIntegrationService()

client = None

def get_openai_client():
    """Get or create OpenAI client"""
    global client
    if client is None:
        openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        if openrouter_api_key:
            logger.info(f"🔑 OpenRouter API key found: {openrouter_api_key[:8]}...{openrouter_api_key[-4:]}")
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_api_key,
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
        
        logger.info("🤖 Making OpenRouter API call...")
        
        import asyncio
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    ai_client.chat.completions.create,
                    model="openai/gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional life advisor and data analyst specializing in career and life path projections."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000  
                ),
                timeout=45.0  
            )
            logger.info("OpenRouter API call successful")
        except asyncio.TimeoutError:
            logger.error("❌ OpenRouter API call timed out after 45 seconds")
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
            return ai_data
        else:
            logger.warning(f"❌ Failed to parse AI response with all methods, using fallback data")
            logger.warning(f"Response content: {ai_content}")
            return generate_fallback_data(request)
        
    except Exception as e:
        logger.error(f"❌ AI service error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            logger.error(f"API response status: {getattr(e.response, 'status_code', 'unknown')}")
            logger.error(f"API response text: {getattr(e.response, 'text', 'unknown')}")
        return generate_fallback_data(request)

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