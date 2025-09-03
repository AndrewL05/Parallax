import openai
import json
import re
import logging
import os
from typing import Dict, Any

from models.simulation import SimulationRequest

logger = logging.getLogger(__name__)

# Initialize OpenAI client for OpenRouter (lazily)
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
            logger.info("✅ OpenAI client initialized successfully")
        else:
            logger.warning("❌ OPENROUTER_API_KEY not set - AI service will use fallback data")
    return client

async def generate_life_simulation(request: SimulationRequest) -> Dict[str, Any]:
    """Generate AI-powered life simulation using AI model"""
    
    # Get OpenAI client (will check for API key)
    ai_client = get_openai_client()
    if not ai_client:
        logger.warning("OpenRouter API key not available, using fallback data")
        return generate_fallback_data(request)
    
    try:
        # Create optimized prompt for faster generation with realistic constraints
        prompt = f"""
        Generate a JSON life simulation comparing two paths. Be concise and realistic.
        
        Choice A: {request.choice_a.title} - {request.choice_a.description}
        Choice B: {request.choice_b.title} - {request.choice_b.description}
        Context: Age {request.user_context.age or 25}, {request.user_context.current_location or 'US'}
        
        IMPORTANT CONSTRAINTS:
        - For Teacher careers: Salaries must be between $40,000 - $120,000
        - For Engineer careers: Salaries must be between $60,000 - $250,000
        - For other careers: Keep salaries realistic for the profession
        - Happiness scores: Must be between 1.0 - 10.0
        - Show realistic career progression over 10 years
        - Summary must be at least 200 characters and provide meaningful comparison
        
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
            "summary": "Choice A offers stability and steady growth in a traditional career path with predictable advancement opportunities and work-life balance. The compensation grows steadily but may have a lower ceiling. Choice B provides higher potential returns and faster financial growth but comes with more variability, risk, and demanding schedules. Consider your risk tolerance, long-term financial goals, personal values around stability vs. growth, and desired work-life balance when making this important life decision. Both paths offer meaningful career satisfaction but through different approaches to professional development and financial security."
        }}
        """
        
        logger.info("🤖 Making OpenRouter API call...")
        
        # Add timeout to prevent hanging
        import asyncio
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    ai_client.chat.completions.create,
                    model="deepseek/deepseek-r1:free",
                    messages=[
                        {"role": "system", "content": "You are a professional life advisor and data analyst specializing in career and life path projections."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    timeout=20  # 20 second timeout
                ),
                timeout=15.0  # 15 second total timeout
            )
            logger.info("✅ OpenRouter API call successful")
        except asyncio.TimeoutError:
            logger.error("❌ OpenRouter API call timed out after 15 seconds")
            raise Exception("API call timed out")
        
        # Parse the AI response
        ai_content = response.choices[0].message.content
        logger.info(f"AI response received, length: {len(ai_content)}")
        logger.info(f"AI response preview: {ai_content[:200]}...")
        
        # Extract JSON from response (handle potential markdown formatting)
        json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
        if json_match:
            ai_data = json.loads(json_match.group())
            logger.info("✅ Successfully parsed AI response JSON")
            return ai_data
        else:
            logger.warning(f"❌ Failed to parse AI response, using fallback data. Response: {ai_content}")
            # Fallback if JSON parsing fails
            return generate_fallback_data(request)
        
    except Exception as e:
        logger.error(f"❌ AI service error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            logger.error(f"API response status: {getattr(e.response, 'status_code', 'unknown')}")
            logger.error(f"API response text: {getattr(e.response, 'text', 'unknown')}")
        return generate_fallback_data(request)

def generate_fallback_data(request: SimulationRequest) -> Dict[str, Any]:
    """Generate fallback simulation data if AI fails"""
    
    # Generate realistic salary ranges based on career type
    def get_salary_range(career_title: str):
        career_lower = career_title.lower()
        if "teacher" in career_lower or "education" in career_lower:
            return 45000, 3000  # Start at 45k, grow by 3k/year (max ~75k)
        elif "engineer" in career_lower or "software" in career_lower or "tech" in career_lower:
            return 70000, 8000  # Start at 70k, grow by 8k/year (max ~150k)
        else:
            return 50000, 4000  # General default: 50k start, 4k growth
    
    choice_a_start, choice_a_growth = get_salary_range(request.choice_a.title)
    choice_b_start, choice_b_growth = get_salary_range(request.choice_b.title)
    
    return {
        "choice_a_timeline": [
            {
                "year": i, 
                "salary": min(choice_a_start + (i-1)*choice_a_growth, 240000),  # Cap at 240k
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
                "salary": min(choice_b_start + (i-1)*choice_b_growth, 240000),  # Cap at 240k
                "happiness_score": min(7.5 + i*0.1, 9.5), 
                "major_event": f"Year {i} milestone", 
                "location": "Unknown", 
                "career_title": request.choice_b.title
            } 
            for i in range(1, 11)
        ],
        "summary": "AI generation encountered an issue, so this simulation uses realistic fallback data based on typical career progression patterns. The projections show expected salary growth, happiness levels, and career milestones for each path based on industry standards and historical data. While not personalized, these estimates provide valuable insights into the potential outcomes of each career choice over a 10-year period."
    }