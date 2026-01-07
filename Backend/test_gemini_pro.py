import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("No GEMINI_API_KEY found in .env")
else:
    genai.configure(api_key=api_key)
    print("Testing generate_content with gemini-pro-latest...")
    try:
        model = genai.GenerativeModel('models/gemini-pro-latest')
        response = model.generate_content("Say hello")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing model: {e}")
