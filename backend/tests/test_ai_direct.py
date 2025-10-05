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

from services.ai_service import get_openai_client

async def test_ai():
    client = get_openai_client()
    if not client:
        print('Client not initialized')
        return False
    
    # Test the API with a simple request
    try:
        print('Testing OpenRouter API connection...')
        response = client.chat.completions.create(
            model='mistralai/mistral-7b-instruct:free',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Say "Hello from AI!" in JSON format: {"message": "your response"}'}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        print('API call successful!')
        print('Response content:', response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f'API call failed: {e}')
        print(f'Error type: {type(e).__name__}')
        if hasattr(e, 'response'):
            print(f'Status code: {getattr(e.response, "status_code", "unknown")}')
        return False

# Run the test
if __name__ == "__main__":
    result = asyncio.run(test_ai())
    print(f"Test result: {'PASSED' if result else 'FAILED'}")