import os
import sys
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv

# Add Backend to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load .env
load_dotenv(BASE_DIR / ".env")
from groq import Groq

# Initialize Groq
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("Error: GROQ_API_KEY not found in .env")
    sys.exit(1)

client = Groq(api_key=groq_api_key)

RECIPES_FILE = BASE_DIR / "cooking_assistant" / "rag" / "data" / "recipes_all_merged.json"

PROMPT = """You are a Sri Lankan culinary expert. Provide authentic ingredients and step-by-step instructions for the following Sri Lankan recipe:

Recipe Name: {recipe_name}
Category: {category}

Return ONLY valid JSON in this exact format:
{{
  "ingredients": [
    "500g ...",
    "1 onion, sliced",
    "1 tsp curry powder"
  ],
  "method": "1. ...\\n2. ...\\n3. ...",
  "tips": "...",
  "cultural_note": "..."
}}
"""

def fix_recipes():
    print(f"Loading {RECIPES_FILE}")
    with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    fixed_count = 0
    
    for i, r in enumerate(recipes):
        # Check if incomplete
        ings = r.get('ingredients', [])
        if not ings or (isinstance(ings, list) and isinstance(ings[0], dict) and "Ingredients to be added" in ings[0].get('name', '')):
            
            names = r.get('names', {})
            en_name = names.get('english', '') or names.get('en', '') or r.get('name', 'Unknown')
            cat = r.get('category', 'main dish')
            
            print(f"[{i+1}/{len(recipes)}] Fixing: {en_name}...")
            
            try:
                response = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": "You are a Sri Lankan culinary expert. Output strictly JSON."},
                        {"role": "user", "content": PROMPT.format(recipe_name=en_name, category=cat)}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                
                raw = response.choices[0].message.content.strip()
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                
                if match:
                    data = json.loads(match.group())
                    
                    # Convert simple string array to dict array for consistency
                    formatted_ings = []
                    for ing in data.get('ingredients', []):
                        formatted_ings.append({"name": ing, "amount": ""})
                        
                    r['ingredients'] = formatted_ings
                    r['method'] = data.get('method', '')
                    if data.get('tips'): r['tips'] = data.get('tips')
                    if data.get('cultural_note'): r['cultural_note'] = data.get('cultural_note')
                    
                    print(f"  -> Success!")
                    fixed_count += 1
                else:
                    print(f"  -> Failed to parse JSON")
                    
                time.sleep(2) # rate limit prevention
                
            except Exception as e:
                print(f"  -> Error: {e}")
                time.sleep(5)
                
    if fixed_count > 0:
        print(f"\nSaving {fixed_count} fixed recipes...")
        with open(RECIPES_FILE, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
        print("Done!")
    else:
        print("No recipes needed fixing.")

if __name__ == "__main__":
    fix_recipes()
