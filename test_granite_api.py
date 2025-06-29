#!/usr/bin/env python3
import os
import requests
import json

def test_granite_api():
    """Test IBM Granite API connection"""
    api_key = os.getenv("IBM_API_KEY", "gVlNnx0CgD8YMT813nCKEgYlkux2Grh7sN2K2dI0XKQK")
    project_id = os.getenv("IBM_PROJECT_ID", "08334910-e7ec-4e32-990d-be70ab4159ad")

    if not api_key or not project_id:
        print("Missing API credentials")
        return False

    print(f"Testing with project_id: {project_id[:8]}...")

    try:
        # Get access token
        token_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "grant_type": "urn:iam:grant-type:apikey",
            "apikey": api_key
        }

        print("Getting access token...")
        response = requests.post(token_url, headers=headers, data=data, timeout=10)

        if response.status_code != 200:
            print(f"Token request failed: {response.status_code}")
            print(response.text)
            return False

        access_token = response.json()["access_token"]
        print("Access token obtained successfully")

        # Test text generation
        url = "https://eu-gb.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        test_prompt = """Create a simple 2-question quiz about Programming Fundamentals at Easy difficulty level.

RESPONSE FORMAT (JSON only):
{
    "subject": "Programming Fundamentals",
    "difficulty": "Easy",
    "total_questions": 2,
    "questions": [
        {
            "id": 1,
            "question": "What is a variable?",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "B",
            "explanation": "Explanation here",
            "topic": "Variables"
        }
    ]
}"""

        payload = {
            "input": test_prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 1000,
                "temperature": 0.3,
                "top_p": 0.9
            },
            "model_id": "ibm/granite-3-8b-instruct",
            "project_id": project_id
        }

        print("Testing text generation...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            generated_text = result["results"][0]["generated_text"]
            print("API call successful!")
            print("Generated text:", generated_text[:200] + "...")
            return True
        else:
            print(f"Generation failed: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_granite_api()
