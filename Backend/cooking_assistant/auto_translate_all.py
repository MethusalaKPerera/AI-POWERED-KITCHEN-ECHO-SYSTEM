#!/usr/bin/env python3
"""
Automated Translation Script
Translates ALL ingredients and recipes to Sinhala and Tamil using Google Translate
Note: Requires 'googletrans' package: pip install googletrans==4.0.0-rc1
"""

import json
from pathlib import Path
import time

try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("⚠️ Google Translate not installed!")
    print("Install with: pip install googletrans==4.0.0-rc1 --break-system-packages")

def translate_text(text, dest_language, translator):
    """Translate text to destination language"""
    try:
        if not text or text.strip() == '':
            return ''
        
        result = translator.translate(text, dest=dest_language)
        time.sleep(0.1)  # Rate limiting
        return result.text
    except Exception as e:
        print(f"  ⚠️ Translation error for '{text[:30]}...': {e}")
        return text  # Return original on error

def translate_ingredients():
    """Translate all ingredients to Sinhala and Tamil"""
    
    print("\n" + "="*70)
    print("INGREDIENT TRANSLATION - FULL DATABASE")
    print("="*70 + "\n")
    
    if not TRANSLATOR_AVAILABLE:
        return
    
    translator = Translator()
    db_path = Path('rag/data/ingredient_database.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ingredients = data.get('ingredients', [])
    total = len(ingredients)
    
    print(f"Translating {total} ingredients...")
    print("This will take approximately {:.1f} minutes\n".format(total * 0.2 / 60))
    
    translated_count = 0
    
    for i, ing in enumerate(ingredients, 1):
        name = ing.get('name', '')
        
        # Skip if already translated
        if ing.get('name_sinhala') and ing.get('name_tamil'):
            print(f"[{i}/{total}] ✓ {name} (already translated)")
            continue
        
        print(f"[{i}/{total}] Translating: {name}")
        
        # Translate to Sinhala
        if not ing.get('name_sinhala'):
            sinhala = translate_text(name, 'si', translator)
            ing['name_sinhala'] = sinhala
            print(f"  සිංහල: {sinhala}")
        
        # Translate to Tamil
        if not ing.get('name_tamil'):
            tamil = translate_text(name, 'ta', translator)
            ing['name_tamil'] = tamil
            print(f"  தமிழ்: {tamil}")
        
        translated_count += 1
        
        # Save progress every 50 ingredients
        if i % 50 == 0:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n  💾 Progress saved ({i}/{total})\n")
    
    # Final save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Translated {translated_count} ingredients!")
    print(f"✅ Saved to: {db_path}")

def translate_recipes():
    """Translate all recipe instructions and descriptions"""
    
    print("\n" + "="*70)
    print("RECIPE TRANSLATION - INSTRUCTIONS & DESCRIPTIONS")
    print("="*70 + "\n")
    
    if not TRANSLATOR_AVAILABLE:
        return
    
    translator = Translator()
    db_path = Path('rag/data/recipes/recipe_database.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    recipes = data.get('recipes', [])
    total = len(recipes)
    
    print(f"Translating {total} recipes...")
    print("This will take approximately {:.1f} minutes\n".format(total * 1.5 / 60))
    
    for i, recipe in enumerate(recipes, 1):
        name = recipe.get('name', '')
        
        # Skip if already has translations
        if recipe.get('description_sinhala') and recipe.get('description_tamil'):
            print(f"[{i}/{total}] ✓ {name} (already translated)")
            continue
        
        print(f"[{i}/{total}] Translating: {name}")
        
        # Translate description
        desc = recipe.get('description', '')
        if desc and not recipe.get('description_sinhala'):
            recipe['description_sinhala'] = translate_text(desc, 'si', translator)
        if desc and not recipe.get('description_tamil'):
            recipe['description_tamil'] = translate_text(desc, 'ta', translator)
        
        # Translate cultural notes
        notes = recipe.get('cultural_notes', '')
        if notes and not recipe.get('cultural_notes_sinhala'):
            recipe['cultural_notes_sinhala'] = translate_text(notes, 'si', translator)
        if notes and not recipe.get('cultural_notes_tamil'):
            recipe['cultural_notes_tamil'] = translate_text(notes, 'ta', translator)
        
        # Optional: Translate instructions (can be time-consuming)
        # Uncomment if you want full instruction translation
        # if not recipe.get('instructions_sinhala'):
        #     recipe['instructions_sinhala'] = [translate_text(inst, 'si', translator) for inst in recipe.get('instructions', [])]
        # if not recipe.get('instructions_tamil'):
        #     recipe['instructions_tamil'] = [translate_text(inst, 'ta', translator) for inst in recipe.get('instructions', [])]
        
        # Save progress every 25 recipes
        if i % 25 == 0:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n  💾 Progress saved ({i}/{total})\n")
    
    # Final save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ All recipes translated!")
    print(f"✅ Saved to: {db_path}")

def main():
    """Main translation workflow"""
    
    print("\n" + "="*70)
    print("AUTOMATED TRANSLATION SYSTEM")
    print("English → Sinhala & Tamil")
    print("="*70)
    
    if not TRANSLATOR_AVAILABLE:
        print("\n❌ Google Translate library not installed!")
        print("\nInstall with:")
        print("  pip install googletrans==4.0.0-rc1 --break-system-packages")
        return
    
    print("\nThis script will translate:")
    print("  • 262 ingredients (names)")
    print("  • 152 recipes (descriptions, cultural notes)")
    print("\nEstimated time: 60-90 minutes")
    print("\nPress Ctrl+C to cancel at any time (progress is saved)")
    
    input("\nPress Enter to start translation...")
    
    # Step 1: Translate ingredients
    translate_ingredients()
    
    # Step 2: Translate recipes
    translate_recipes()
    
    print("\n" + "="*70)
    print("✅ TRANSLATION COMPLETE!")
    print("="*70)
    print("\nAll ingredients and recipes now have Sinhala & Tamil translations!")
    print("\nNext steps:")
    print("  1. Update PP1 materials: python pp1_preparation.py")
    print("  2. Rebuild RAG: python recipe_rag_system.py")
    print("  3. Test multilingual: python test_multilingual.py")

if __name__ == "__main__":
    main()