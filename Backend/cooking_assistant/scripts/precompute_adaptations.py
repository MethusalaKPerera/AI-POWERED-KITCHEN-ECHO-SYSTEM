import os
import sys
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")
from groq import Groq

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("Error: GROQ_API_KEY not found in .env")
    sys.exit(1)

client = Groq(api_key=groq_api_key)

RECIPES_FILE = BASE_DIR / "cooking_assistant" / "rag" / "data" / "recipes_all_merged.json"

PROMPT = """You are a Sri Lankan culinary expert.
Look at the exact ingredients required for this recipe:

Recipe: {recipe_name}
Ingredients: {ingredients}

Identify 2 to 4 ingredients from this specific list that might be difficult to find for someone living outside of Sri Lanka (e.g., Goraka, Maldive Fish, Rampe/Pandan, specific local veggies). 
For EACH of these hard-to-find ingredients, suggest a common, easy-to-find substitute.

Return ONLY valid JSON in this exact format (no extra text):
{{
  "adaptive_ingredients": [
    {{
      "original": "Maldive Fish",
      "substitute": "Soy sauce or anchovy paste",
      "notes": "Adds the necessary umami flavor."
    }}
  ]
}}
"""

def precompute_adaptations():
    print(f"Loading {RECIPES_FILE}")
    with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    updated_count = 0
    
    # Process only the first 20 recipes to avoid huge API wait times right now.
    # The user can run it again later for all of them.
    recipes_to_process = recipes[:180]
    
    for i, r in enumerate(recipes_to_process):
        names = r.get('names', {})
        en_name = names.get('english', '') or names.get('en', '') or r.get('name', 'Unknown')
        
        if 'adaptive_ingredients' in r:
            print(f"[{i+1}/{len(recipes_to_process)}] {en_name} already has adaptive ingredients, skipping.")
            continue
            
        ings = r.get('ingredients', [])
        if not ings or (isinstance(ings, list) and isinstance(ings[0], dict) and "Ingredients to be added" in ings[0].get('name', '')):
            print(f"[{i+1}/{len(recipes_to_process)}] {en_name} has no ingredients, skipping.")
            continue
            
        ing_texts = []
        for ing in ings:
            if isinstance(ing, dict):
                ing_texts.append(ing.get('name', ''))
            else:
                ing_texts.append(str(ing))
                
        print(f"[{i+1}/{len(recipes_to_process)}] Generating adaptations for: {en_name}...")
        
        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are an AI assistant. Output ONLY JSON."},
                    {"role": "user", "content": PROMPT.format(recipe_name=en_name, ingredients=", ".join(ing_texts))}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            raw = response.choices[0].message.content.strip()
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            
            if match:
                data = json.loads(match.group())
                
                # Filter out useless ones like "Chicken -> Tofu" unless it's genuinely hard to find.
                # Actually, we trust the LLM.
                adaps = data.get('adaptive_ingredients', [])
                if adaps:
                    r['adaptive_ingredients'] = adaps
                    print(f"  -> Generated {len(adaps)} adaptations.")
                    updated_count += 1
                else:
                    print(f"  -> No adaptations needed.")
                    r['adaptive_ingredients'] = []
            else:
                print(f"  -> Failed to parse JSON")
                
            time.sleep(1) # rate limit prevention
            
        except Exception as e:
            print(f"  -> Error: {e}")
            time.sleep(3)
            
    if updated_count > 0:
        print(f"\nSaving updated recipes...")
        with open(RECIPES_FILE, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
        print("Done!")
    else:
        print("No updates made.")

if __name__ == "__main__":
    precompute_adaptations()
