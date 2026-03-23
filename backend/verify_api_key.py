import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment.")
    sys.exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-4:]}")

try:
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    print("Listing available models...")
    models = client.models.list()
    for m in models.data:
        print(f"- {m.id}")

    # Test with a known stable model if available, or just the first one
    model_id = "llama-3.1-8b-instant" # Default fallback
    if models.data:
        model_id = models.data[0].id
    
    print(f"\nTesting with model: {model_id}")
    response = client.chat.completions.create(
        model=model_id, 
        messages=[{"role": "user", "content": "Test."}],
        max_tokens=5
    )
    print("Success: API Key is valid and working!")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"Error: API Key verification failed. {str(e)}")
    sys.exit(1)
