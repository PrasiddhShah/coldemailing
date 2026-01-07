
from config import load_config
import os

try:
    config = load_config()
    print(f"Loaded LLM_MODEL: {config.LLM_MODEL}")
    
    # Optional: Check if we can import the lib
    from google import genai
    print("google-genai imported successfully")
except Exception as e:
    print(f"Error: {e}")
