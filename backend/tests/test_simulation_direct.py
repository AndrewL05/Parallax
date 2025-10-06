#!/usr/bin/env python3
import requests
import json

# Test simulation data
simulation_data = {
    "choice_a": {
        "title": "Teacher",
        "description": "Become a high school teacher with a focus on education",
        "category": "career"
    },
    "choice_b": {
        "title": "Engineer", 
        "description": "Pursue a career as a software engineer at a tech company",
        "category": "career"
    },
    "user_context": {
        "age": 28,
        "current_location": "Chicago",
        "education_level": "bachelors"
    }
}

print("Testing simulation endpoint...")
response = requests.post(
    "http://localhost:8000/api/simulate",
    json=simulation_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Summary preview: {data['summary'][:100]}...")
    print(f"Choice A first year salary: ${data['choice_a_timeline'][0]['salary']}")
    print(f"Choice B first year salary: ${data['choice_b_timeline'][0]['salary']}")
else:
    print(f"Error: {response.text}")