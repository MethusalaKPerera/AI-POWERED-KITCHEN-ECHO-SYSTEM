"""
Translation Script for 200 Sri Lankan Recipes
Uses googletrans to translate English recipes to Sinhala and Tamil
"""
import json
import os
import time
import sys

try:
    from googletrans import Translator
except ImportError:
    print("Installing googletrans...")
    os.system("pip install googletrans==4.0.0rc1")
    from googletrans import Translator

# Translation cache to avoid re-translating same terms
_cache = {}

def translate_text(translator, text, dest_lang, retries=3):
    """Translate text with caching, retries, and error handling"""
    if not text or not text.strip():
        return text, True
    
    cache_key = f"{text}|{dest_lang}"
    if cache_key in _cache:
        return _cache[cache_key], True
    
    for attempt in range(retries):
        try:
            result = translator.translate(text, dest=dest_lang)
            translated = result.text
            _cache[cache_key] = translated
            return translated, True
        except Exception as e:
            if attempt < retries - 1:
                wait = (attempt + 1) * 2
                print(f"    Retry {attempt+1}/{retries} for '{text[:30]}...' ({e}), waiting {wait}s")
                time.sleep(wait)
            else:
                print(f"    FAILED to translate '{text[:40]}...' to {dest_lang}: {e}")
                return text, False  # Return original on failure

def translate_recipe(translator, recipe, recipe_num, total):
    """Translate a single recipe to Sinhala and Tamil"""
    print(f"Translating recipe {recipe_num}/{total}: {recipe['names']['english']}")
    
    review_flags = []
    translated = json.loads(json.dumps(recipe))  # Deep copy
    
    # Translate recipe name
    si_name, ok_si = translate_text(translator, recipe["names"]["english"], "si")
    ta_name, ok_ta = translate_text(translator, recipe["names"]["english"], "ta")
    translated["names"]["sinhala"] = si_name
    translated["names"]["tamil"] = ta_name
    if not ok_si or not ok_ta:
        review_flags.append({"field": "name", "english": recipe["names"]["english"]})
    time.sleep(0.5)
    
    # Translate ingredient names
    for i, ing in enumerate(translated["ingredients"]):
        si_ing, ok1 = translate_text(translator, ing["name"], "si")
        ta_ing, ok2 = translate_text(translator, ing["name"], "ta")
        translated["ingredients"][i]["names"] = {
            "english": ing["name"],
            "sinhala": si_ing,
            "tamil": ta_ing
        }
        if not ok1 or not ok2:
            review_flags.append({"field": f"ingredient[{i}]", "english": ing["name"]})
        time.sleep(0.3)
    
    # Translate method
    si_method, ok1 = translate_text(translator, recipe["method"], "si")
    ta_method, ok2 = translate_text(translator, recipe["method"], "ta")
    translated["method_translations"] = {
        "english": recipe["method"],
        "sinhala": si_method,
        "tamil": ta_method
    }
    if not ok1 or not ok2:
        review_flags.append({"field": "method", "english": recipe["method"][:50]})
    time.sleep(0.5)
    
    # Translate tips
    si_tips, ok1 = translate_text(translator, recipe["tips"], "si")
    ta_tips, ok2 = translate_text(translator, recipe["tips"], "ta")
    translated["tips_translations"] = {
        "english": recipe["tips"],
        "sinhala": si_tips,
        "tamil": ta_tips
    }
    if not ok1 or not ok2:
        review_flags.append({"field": "tips", "english": recipe["tips"][:50]})
    time.sleep(0.3)
    
    # Translate cultural note
    si_note, ok1 = translate_text(translator, recipe["cultural_note"], "si")
    ta_note, ok2 = translate_text(translator, recipe["cultural_note"], "ta")
    translated["cultural_note_translations"] = {
        "english": recipe["cultural_note"],
        "sinhala": si_note,
        "tamil": ta_note
    }
    if not ok1 or not ok2:
        review_flags.append({"field": "cultural_note", "english": recipe["cultural_note"][:50]})
    time.sleep(0.3)
    
    return translated, review_flags

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Translate recipes to Sinhala and Tamil")
    parser.add_argument("--dry-run", action="store_true", help="Only translate first 2 recipes")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of recipes")
    parser.add_argument("--input", default=None, help="Input JSON file path")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "cooking_assistant", "rag", "data")
    
    input_path = args.input or os.path.join(data_dir, "new_200_recipes.json")
    output_path = args.output or os.path.join(data_dir, "recipes_200_translated.json")
    review_path = os.path.join(data_dir, "translation_review_log.json")
    
    # Load recipes
    print(f"Loading recipes from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    
    limit = args.limit or (2 if args.dry_run else len(recipes))
    recipes = recipes[:limit]
    print(f"Translating {len(recipes)} recipes...")
    
    # Initialize translator
    translator = Translator()
    
    translated_recipes = []
    all_review_flags = []
    
    for i, recipe in enumerate(recipes, 1):
        try:
            translated, flags = translate_recipe(translator, recipe, i, len(recipes))
            translated_recipes.append(translated)
            if flags:
                all_review_flags.append({
                    "recipe_id": recipe["id"],
                    "recipe_name": recipe["names"]["english"],
                    "issues": flags
                })
        except Exception as e:
            print(f"  ERROR on recipe {recipe['id']}: {e}")
            translated_recipes.append(recipe)  # Keep original
            all_review_flags.append({
                "recipe_id": recipe["id"],
                "recipe_name": recipe["names"]["english"],
                "issues": [{"field": "entire_recipe", "error": str(e)}]
            })
    
    # Save translated recipes
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated_recipes, f, indent=2, ensure_ascii=False)
    print(f"\nSaved translated recipes to: {output_path}")
    
    # Save review log
    review_log = {
        "total_recipes": len(translated_recipes),
        "recipes_with_issues": len(all_review_flags),
        "cache_hits": len(_cache),
        "flagged_recipes": all_review_flags
    }
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review_log, f, indent=2, ensure_ascii=False)
    print(f"Saved review log to: {review_path}")
    print(f"Recipes with translation issues: {len(all_review_flags)}/{len(translated_recipes)}")

if __name__ == "__main__":
    main()
