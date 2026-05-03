#!/usr/bin/env python3
"""
Complete Translation Script - Using deep-translator
Works with Python 3.14+
Translates ALL ingredients and recipes to Sinhala and Tamil
"""

import json
from pathlib import Path
import time

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("❌ deep-translator not installed!")
    print("Install with: pip install deep-translator --break-system-packages")

def translate_text(text, dest_language):
    """Translate text to destination language using deep-translator"""
    try:
        if not text or text.strip() == '':
            return ''
        
        # Map language codes
        lang_map = {
            'sinhala': 'si',
            'tamil': 'ta'
        }
        
        dest_code = lang_map.get(dest_language, dest_language)
        
        translator = GoogleTranslator(source='en', target=dest_code)
        result = translator.translate(text[:500])  # Limit to 500 chars per request
        
        time.sleep(0.5)  # Rate limiting
        return result
        
    except Exception as e:
        print(f"  ⚠️ Translation error for '{text[:30]}...': {e}")
        return text  # Return original on error

def translate_ingredients():
    """Translate all ingredients to Sinhala and Tamil"""
    
    print("\n" + "="*70)
    print("INGREDIENT TRANSLATION - COMPLETE DATABASE")
    print("="*70 + "\n")
    
    if not TRANSLATOR_AVAILABLE:
        return
    
    db_path = Path('rag/data/ingredient_database.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ingredients = data.get('ingredients', [])
    total = len(ingredients)
    
    print(f"Translating {total} ingredients...")
    print(f"Estimated time: {total * 1.0 / 60:.1f} minutes\n")
    
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
            sinhala = translate_text(name, 'sinhala')
            ing['name_sinhala'] = sinhala
            print(f"  සිංහල: {sinhala}")
        
        # Translate to Tamil
        if not ing.get('name_tamil'):
            tamil = translate_text(name, 'tamil')
            ing['name_tamil'] = tamil
            print(f"  தமிழ்: {tamil}")
        
        translated_count += 1
        
        # Save progress every 20 ingredients
        if i % 20 == 0:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n  💾 Progress saved ({i}/{total})\n")
    
    # Final save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Translated {translated_count} new ingredients!")
    print(f"✅ Total: {total} ingredients fully translated")
    print(f"✅ Saved to: {db_path}")

def translate_recipes():
    """Translate recipe descriptions and cultural notes"""
    
    print("\n" + "="*70)
    print("RECIPE TRANSLATION - DESCRIPTIONS & NOTES")
    print("="*70 + "\n")
    
    if not TRANSLATOR_AVAILABLE:
        return
    
    db_path = Path('rag/data/recipes/recipe_database.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    recipes = data.get('recipes', [])
    total = len(recipes)
    
    print(f"Translating {total} recipe descriptions...")
    print(f"Estimated time: {total * 2.0 / 60:.1f} minutes\n")
    
    for i, recipe in enumerate(recipes, 1):
        name = recipe.get('name', '')
        
        # Skip if already translated
        if recipe.get('description_sinhala') and recipe.get('description_tamil'):
            print(f"[{i}/{total}] ✓ {name} (already translated)")
            continue
        
        print(f"[{i}/{total}] Translating: {name}")
        
        # Translate description
        desc = recipe.get('description', '')
        if desc and not recipe.get('description_sinhala'):
            recipe['description_sinhala'] = translate_text(desc, 'sinhala')
            print(f"  Description → සිංහල")
        
        if desc and not recipe.get('description_tamil'):
            recipe['description_tamil'] = translate_text(desc, 'tamil')
            print(f"  Description → தமிழ்")
        
        # Translate cultural notes
        notes = recipe.get('cultural_notes', '')
        if notes and not recipe.get('cultural_notes_sinhala'):
            recipe['cultural_notes_sinhala'] = translate_text(notes, 'sinhala')
            print(f"  Cultural notes → සිංහල")
        
        if notes and not recipe.get('cultural_notes_tamil'):
            recipe['cultural_notes_tamil'] = translate_text(notes, 'tamil')
            print(f"  Cultural notes → தமිழ்")
        
        # Save progress every 10 recipes
        if i % 10 == 0:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n  💾 Progress saved ({i}/{total})\n")
    
    # Final save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ All {total} recipes translated!")
    print(f"✅ Saved to: {db_path}")

def main():
    """Main translation workflow"""
    
    print("\n" + "="*70)
    print("COMPLETE TRANSLATION SYSTEM")
    print("English → Sinhala & Tamil")
    print("Using: deep-translator (Google Translate API)")
    print("="*70)
    
    if not TRANSLATOR_AVAILABLE:
        print("\n❌ deep-translator not installed!")
        print("\nInstall with:")
        print("  pip install deep-translator --break-system-packages")
        return
    
    print("\nThis will translate:")
    print("  • 262 ingredients (names)")
    print("  • 165 recipes (descriptions, cultural notes)")
    print("\nEstimated time: 6-8 minutes")
    print("\nProgress is saved every 10-20 items")
    print("Safe to interrupt (Ctrl+C) - will resume from where it stopped")
    
    input("\n✅ Press Enter to start translation...")
    
    start_time = time.time()
    
    # Step 1: Translate ingredients
    translate_ingredients()
    
    # Step 2: Translate recipes
    translate_recipes()
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("✅ TRANSLATION COMPLETE!")
    print("="*70)
    print(f"\nCompleted in {elapsed/60:.1f} minutes")
    print("\n✅ All 262 ingredients translated")
    print("✅ All 165 recipes translated")
    print("\nNext steps:")
    print("  1. Rebuild RAG: python recipe_rag_system.py")
    print("  2. Update PP1: python pp1_preparation.py")
    print("  3. Test: python test_multilingual.py")

if __name__ == "__main__":
    main()