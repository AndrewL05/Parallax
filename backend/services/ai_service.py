import openai
import json
import re
import logging
import os
from typing import Dict, Any

from ..models.simulation import SimulationRequest

logger = logging.getLogger(__name__)

# Initialize OpenAI client for OpenRouter
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get('OPENROUTER_API_KEY'),
)

async def generate_life_simulation(request: SimulationRequest) -> Dict[str, Any]:
    """Generate AI-powered life simulation using Deepseek model"""
    
    try:
        # Create optimized prompt for faster generation
        prompt = f"""
        Generate a JSON life simulation comparing two paths. Be concise and realistic.
        
        Choice A: {request.choice_a.title} - {request.choice_a.description}
        Choice B: {request.choice_b.title} - {request.choice_b.description}
        Context: Age {request.user_context.age or 25}, {request.user_context.current_location or 'US'}
        
        Return ONLY valid JSON in this exact format:
        {{
            "choice_a_timeline": [
                {{"year": 1, "salary": 75000, "happiness_score": 7.5, "major_event": "Started new position", "location": "City", "career_title": "Job Title"}},
                {{"year": 2, "salary": 78000, "happiness_score": 7.8, "major_event": "Promotion", "location": "City", "career_title": "Senior Job Title"}},
                {{"year": 3, "salary": 82000, "happiness_score": 8.0, "major_event": "Skill development", "location": "City", "career_title": "Senior Job Title"}},
                {{"year": 4, "salary": 87000, "happiness_score": 8.2, "major_event": "Team lead role", "location": "City", "career_title": "Lead Title"}},
                {{"year": 5, "salary": 92000, "happiness_score": 8.1, "major_event": "Major project success", "location": "City", "career_title": "Lead Title"}},
                {{"year": 6, "salary": 98000, "happiness_score": 8.3, "major_event": "Management role", "location": "City", "career_title": "Manager Title"}},
                {{"year": 7, "salary": 105000, "happiness_score": 8.5, "major_event": "Department growth", "location": "City", "career_title": "Manager Title"}},
                {{"year": 8, "salary": 112000, "happiness_score": 8.4, "major_event": "Strategic planning", "location": "City", "career_title": "Senior Manager"}},
                {{"year": 9, "salary": 120000, "happiness_score": 8.6, "major_event": "Executive role", "location": "City", "career_title": "Director"}},
                {{"year": 10, "salary": 130000, "happiness_score": 8.8, "major_event": "Industry recognition", "location": "City", "career_title": "Director"}}
            ],
            "choice_b_timeline": [
                {{"year": 1, "salary": 65000, "happiness_score": 8.0, "major_event": "New venture start", "location": "City", "career_title": "Entrepreneur"}},
                {{"year": 2, "salary": 70000, "happiness_score": 7.5, "major_event": "Client acquisition", "location": "City", "career_title": "Founder"}},
                {{"year": 3, "salary": 68000, "happiness_score": 7.8, "major_event": "Market challenges", "location": "City", "career_title": "Founder"}},
                {{"year": 4, "salary": 85000, "happiness_score": 8.5, "major_event": "Business growth", "location": "City", "career_title": "CEO"}},
                {{"year": 5, "salary": 95000, "happiness_score": 8.7, "major_event": "Team expansion", "location": "City", "career_title": "CEO"}},
                {{"year": 6, "salary": 110000, "happiness_score": 8.9, "major_event": "Major contract", "location": "City", "career_title": "CEO"}},
                {{"year": 7, "salary": 125000, "happiness_score": 8.6, "major_event": "Market expansion", "location": "City", "career_title": "CEO"}},
                {{"year": 8, "salary": 140000, "happiness_score": 8.8, "major_event": "Strategic partnerships", "location": "City", "career_title": "CEO"}},
                {{"year": 9, "salary": 160000, "happiness_score": 9.0, "major_event": "Industry leadership", "location": "City", "career_title": "CEO"}},
                {{"year": 10, "salary": 180000, "happiness_score": 9.2, "major_event": "Exit opportunity", "location": "City", "career_title": "CEO"}}
            ],
            "summary": "Choice A offers stability and steady growth in a traditional career path, while Choice B provides higher potential returns but with more variability and risk. Consider your risk tolerance and long-term goals."
        }}
        """
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "system", "content": "You are a professional life advisor and data analyst specializing in career and life path projections."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        # Parse the AI response
        ai_content = response.choices[0].message.content
        logger.info(f"AI response received, length: {len(ai_content)}")
        
        # Extract JSON from response (handle potential markdown formatting)
        json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
        if json_match:
            ai_data = json.loads(json_match.group())
            logger.info("Successfully parsed AI response JSON")
            return ai_data
        else:
            logger.warning("Failed to parse AI response, using fallback data")
            # Fallback if JSON parsing fails
            return generate_fallback_data(request)
        
    except Exception as e:
        logger.error(f"AI service error: {e}")
        return generate_fallback_data(request)

def generate_fallback_data(request: SimulationRequest) -> Dict[str, Any]:
    """Generate fallback simulation data if AI fails"""
    return {
        "choice_a_timeline": [
            {"year": i, "salary": 70000 + i*5000, "happiness_score": 7.0 + i*0.1, "major_event": f"Year {i} milestone", "location": "Unknown", "career_title": request.choice_a.title} 
            for i in range(1, 11)
        ],
        "choice_b_timeline": [
            {"year": i, "salary": 65000 + i*4000, "happiness_score": 7.5 + i*0.1, "major_event": f"Year {i} milestone", "location": "Unknown", "career_title": request.choice_b.title} 
            for i in range(1, 11)
        ],
        "summary": "AI generation encountered an issue. This is a fallback simulation with basic projections."
    }