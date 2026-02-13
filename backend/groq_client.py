import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    print("WARNING: GROQ_API_KEY not found in environment variables.")
    client = None
