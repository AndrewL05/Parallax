#!/usr/bin/env python3
import asyncio
import sys
import os
from dotenv import load_dotenv
import openai
import json

# Load environment variables
load_dotenv('backend/.env')
load_dotenv('.env')

async def debug_ai_call():
    openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
    if not openrouter_api_key:
        print("No API key found")
        return
    
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )
    
    simple_prompt = """Generate a JSON response for comparing two career paths:
    
    Teacher vs Engineer
    
    Return ONLY valid JSON in this format:
    {
        "choice_a_timeline": [{"year": 1, "salary": 50000, "happiness_score": 7.5, "major_event": "Started teaching", "location": "City", "career_title": "Teacher"}],
        "choice_b_timeline": [{"year": 1, "salary": 70000, "happiness_score": 8.0, "major_event": "Started engineering", "location": "City", "career_title": "Engineer"}],
        "summary": "Comparison of teaching vs engineering career paths."
    }
    """
    
    try:
        print("Making simple API call...")
        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.chat.completions.create,
                model="mistralai/mistral-7b-instruct:free",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Return only valid JSON."},
                    {"role": "user", "content": simple_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            ),
            timeout=60.0
        )
        
        content = response.choices[0].message.content
        print(f"Response received (length: {len(content)}):")
        print(content)
        print("\n" + "="*50)
        
        # Try to parse as JSON
        try:
            data = json.loads(content.strip())
            print("Successfully parsed as JSON!")
            return True
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            return False
            
    except Exception as e:
        print(f"API call failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    result = asyncio.run(debug_ai_call())