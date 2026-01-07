import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("No API Key found in .env")
    exit(1)

# Initialize client with API key
client = genai.Client(api_key=api_key)

print("Listing available models...")
try:
    models = client.models.list()
    for m in models:
        print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
