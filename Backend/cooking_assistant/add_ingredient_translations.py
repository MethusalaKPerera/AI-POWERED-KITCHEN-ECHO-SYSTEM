#!/usr/bin/env python3
"""
Add Sinhala and Tamil translations to ingredient database
Uses basic translations for common ingredients
"""

import json
from pathlib import Path

# Common ingredient translations (manually curated for accuracy)
TRANSLATIONS = {
    'chicken': {
        'sinhala': 'කුකුල් මස්',
        'tamil': 'கோழி'
    },
    'coconut milk': {
        'sinhala': 'කිරි',
        'tamil': 'தேங்காய் பால்'
    },
    'coconut': {
        'sinhala': 'පොල්',
        'tamil': 'தேங்காய்'
    },
    'rice': {
        'sinhala': 'බත්',
        'tamil': 'அரிசி'
    },
    'curry powder': {
        'sinhala': 'කරපිංචා',
        'tamil': 'கறி பொடி'
    },
    'chili powder': {
        'sinhala': 'මිරිස් කුඩු',
        'tamil': 'மிளகாய் தூள்'
    },
    'onion': {
        'sinhala': 'ලූනු',
        'tamil': 'வெங்காயம்'
    },
    'onions': {
        'sinhala': 'ලූනු',
        'tamil': 'வெங்காயம்'
    },
    'garlic': {
        'sinhala': 'සුදුලූනු',
        'tamil': 'பூண்டு'
    },
    'ginger': {
        'sinhala': 'ඉඟුරු',
        'tamil': 'இஞ்சி'
    },
    'turmeric': {
        'sinhala': 'කහ',
        'tamil': 'மஞ்சள்'
    },
    'curry leaves': {
        'sinhala': 'කරපිංචා',
        'tamil': 'கருவேப்பிலை'
    },
    'salt': {
        'sinhala': 'ලුණු',
        'tamil': 'உப்பு'
    },
    'oil': {
        'sinhala': 'තෙල්',
        'tamil': 'எண்ணெய்'
    },
    'fish': {
        'sinhala': 'මාලු',
        'tamil': 'மீன்'
    },
    'potato': {
        'sinhala': 'අල',
        'tamil': 'உருளைக்கிழங்கு'
    },
    'tomato': {
        'sinhala': 'තක්කාලි',
        'tamil': 'தக்காளி'
    },
    'tomatoes': {
        'sinhala': 'තක්කාලි',
        'tamil': 'தக்காளி'
    },
    'green chilies': {
        'sinhala': 'අබ මිරිස්',
        'tamil': 'பச்சை மிளகாய்'
    },
    'jaggery': {
        'sinhala': 'හකුරු',
        'tamil': 'வெல்லம்'
    },
    'rice flour': {
        'sinhala': 'හාල් පිටි',
        'tamil': 'அரிசி மாவு'
    },
    'sugar': {
        'sinhala': 'සීනි',
        'tamil': 'சர்க்கரை'
    },
    'eggs': {
        'sinhala': 'බිත්තර',
        'tamil': 'முட்டை'
    },
    'lime': {
        'sinhala': 'දෙහි',
        'tamil': 'எலுமிச்சை'
    },
    'mustard seeds': {
        'sinhala': 'අබ',
        'tamil': 'கடுகு'
    },
    'cashews': {
        'sinhala': 'කජු',
        'tamil': 'முந்திரி'
    },
    'cardamom': {
        'sinhala': 'එනසාල',
        'tamil': 'ஏலக்காய்'
    },
    'cinnamon': {
        'sinhala': 'කුරුඳු',
        'tamil': 'பட்டை'
    },
    'cloves': {
        'sinhala': 'කරාබු නැටි',
        'tamil': 'கிராம்பு'
    }
}

def translate_ingredients():
    """Add translations to ingredient database"""
    
    db_path = Path('rag/data/ingredient_database.json')
    
    print("\n" + "="*70)
    print("INGREDIENT TRANSLATION UPDATER")
    print("="*70 + "\n")
    
    # Load current database
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ingredients = data.get('ingredients', [])
    print(f"Loaded {len(ingredients)} ingredients")
    
    # Update with translations
    updated_count = 0
    for ing in ingredients:
        name = ing.get('name', '').lower()
        
        if name in TRANSLATIONS:
            ing['name_sinhala'] = TRANSLATIONS[name]['sinhala']
            ing['name_tamil'] = TRANSLATIONS[name]['tamil']
            updated_count += 1
        else:
            # Keep empty for manual translation later
            if 'name_sinhala' not in ing or not ing['name_sinhala']:
                ing['name_sinhala'] = ''
            if 'name_tamil' not in ing or not ing['name_tamil']:
                ing['name_tamil'] = ''
    
    # Save updated database
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated_count} ingredients with translations")
    print(f"✅ {len(ingredients) - updated_count} ingredients still need manual translation")
    print(f"\nTranslated ingredients include:")
    
    translated = [ing['name'] for ing in ingredients if ing.get('name_sinhala')]
    for i, name in enumerate(translated[:10], 1):
        ing = next(ing for ing in ingredients if ing['name'].lower() == name.lower())
        print(f"  {i}. {ing['name']} = {ing['name_sinhala']} = {ing['name_tamil']}")
    
    if len(translated) > 10:
        print(f"  ... and {len(translated) - 10} more")
    
    print(f"\n✅ Saved to: {db_path}")
    print("\n" + "="*70)

if __name__ == "__main__":
    translate_ingredients()