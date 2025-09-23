#!/usr/bin/env python3
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')
load_dotenv('.env')

# Add the backend directory to Python path
sys.path.append('backend')

from services.ai_service import generate_life_simulation
from models.simulation import SimulationRequest, LifeChoice, UserContext

async def test_full_simulation():
    # Create test request
    request = SimulationRequest(
        choice_a=LifeChoice(
            title="Teacher",
            description="Become a high school teacher with a focus on education",
            category="career"
        ),
        choice_b=LifeChoice(
            title="Engineer", 
            description="Pursue a career as a software engineer at a tech company",
            category="career"
        ),
        user_context=UserContext(
            age=28,
            current_location="Chicago",
            education_level="bachelors"
        )
    )
    
    print("Testing full AI simulation...")
    
    # First test the AI client directly
    from services.ai_service import get_openai_client
    client = get_openai_client()
    print(f"Client initialized: {client is not None}")
    
    try:
        result = await generate_life_simulation(request)
        print(f"Summary: {result['summary'][:100]}...")
        print(f"Is fallback data: {'AI generation encountered an issue' in result['summary']}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# Run the test
if __name__ == "__main__":
    result = asyncio.run(test_full_simulation())