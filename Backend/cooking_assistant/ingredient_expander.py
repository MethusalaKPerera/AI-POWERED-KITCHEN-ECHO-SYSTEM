#!/usr/bin/env python3
"""
Ingredient Database Expander
Extracts ALL unique ingredients from recipes and builds comprehensive ingredient database
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def extract_ingredient_name(ingredient_text):
    """Extract clean ingredient name from full text"""
    # Remove measurements and descriptors
    # e.g., "500g chicken, cubed" -> "chicken"
    
    # Remove common measurements
    cleaned = re.sub(r'\d+\s*(g|kg|ml|l|cups?|tbsp|tsp|oz|lb|pieces?|inch)', '', ingredient_text, flags=re.IGNORECASE)
    
    # Remove parenthetical descriptions
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    
    # Remove commas and everything after
    cleaned = cleaned.split(',')[0]
    
    # Remove leading/trailing spaces and common words
    cleaned = cleaned.strip()
    cleaned = re.sub(r'^(sliced|chopped|diced|minced|crushed|grated|ground|fresh|dried|raw|cooked)\s+', '', cleaned, flags=re.IGNORECASE)
    
    # Get first 1-3 words (main ingredient)
    words = cleaned.split()
    if len(words) <= 3:
        return ' '.join(words).lower()
    else:
        return ' '.join(words[:2]).lower()

def categorize_ingredient(ingredient):
    """Categorize ingredient by type"""
    ingredient_lower = ingredient.lower()
    
    # Spices
    spices = ['curry', 'chili', 'turmeric', 'cumin', 'coriander', 'cinnamon', 'cardamom', 
              'cloves', 'pepper', 'mustard', 'fennel', 'fenugreek', 'nutmeg', 'saffron',
              'garam masala', 'curry powder', 'curry leaves']
    
    # Proteins
    proteins = ['chicken', 'fish', 'beef', 'prawn', 'cuttlefish', 'egg', 'dal', 'lentil',
                'maldive fish', 'cashew', 'mung']
    
    # Vegetables
    vegetables = ['onion', 'garlic', 'ginger', 'tomato', 'potato', 'carrot', 'bean',
                  'brinjal', 'beetroot', 'leek', 'chili', 'capsicum', 'pepper',
                  'gotu kola', 'jackfruit', 'cucumber']
    
    # Dairy & Liquids
    dairy = ['coconut milk', 'milk', 'yogurt', 'curd', 'cream', 'butter', 'ghee']
    
    # Staples
    staples = ['rice', 'flour', 'bread', 'oil', 'salt', 'sugar', 'jaggery', 'treacle',
               'vinegar', 'tamarind', 'goraka', 'lime', 'water']
    
    # Check categories
    for spice in spices:
        if spice in ingredient_lower:
            return 'Spices & Seasonings'
    
    for protein in proteins:
        if protein in ingredient_lower:
            return 'Proteins'
    
    for veg in vegetables:
        if veg in ingredient_lower:
            return 'Vegetables'
    
    for d in dairy:
        if d in ingredient_lower:
            return 'Dairy & Liquids'
    
    for staple in staples:
        if staple in ingredient_lower:
            return 'Staples'
    
    return 'Other'

def build_comprehensive_ingredient_database():
    """Build complete ingredient database from all recipes"""
    
    # Load recipes
    recipe_db_path = Path('rag/data/recipes/recipe_database.json')
    with open(recipe_db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        recipes = data['recipes']
    
    print(f"Processing {len(recipes)} recipes...")
    
    # Extract all ingredients
    ingredient_usage = defaultdict(lambda: {'count': 0, 'recipes': [], 'category': ''})
    
    for recipe in recipes:
        recipe_id = recipe['id']
        recipe_name = recipe['name']
        
        for ingredient_text in recipe.get('ingredients', []):
            # Extract clean name
            ingredient_name = extract_ingredient_name(ingredient_text)
            
            if ingredient_name and len(ingredient_name) > 2:  # Skip very short names
                ingredient_usage[ingredient_name]['count'] += 1
                ingredient_usage[ingredient_name]['recipes'].append({
                    'id': recipe_id,
                    'name': recipe_name,
                    'full_text': ingredient_text
                })
    
    # Categorize ingredients
    for ingredient in ingredient_usage:
        ingredient_usage[ingredient]['category'] = categorize_ingredient(ingredient)
    
    # Build comprehensive database
    ingredient_list = []
    for ingredient, data in sorted(ingredient_usage.items(), key=lambda x: x[1]['count'], reverse=True):
        ingredient_list.append({
            'name': ingredient.title(),
            'name_sinhala': '',  # To be filled manually or via translation
            'name_tamil': '',     # To be filled manually or via translation
            'category': data['category'],
            'usage_count': data['count'],
            'common': data['count'] >= 5,  # Used in 5+ recipes
            'used_in_recipes': len(data['recipes']),
            'example_recipes': [r['name'] for r in data['recipes'][:3]]  # First 3 examples
        })
    
    # Save to file
    output_path = Path('rag/data/ingredient_database_comprehensive.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_ingredients': len(ingredient_list),
            'by_category': {
                'Spices & Seasonings': len([i for i in ingredient_list if i['category'] == 'Spices & Seasonings']),
                'Proteins': len([i for i in ingredient_list if i['category'] == 'Proteins']),
                'Vegetables': len([i for i in ingredient_list if i['category'] == 'Vegetables']),
                'Dairy & Liquids': len([i for i in ingredient_list if i['category'] == 'Dairy & Liquids']),
                'Staples': len([i for i in ingredient_list if i['category'] == 'Staples']),
                'Other': len([i for i in ingredient_list if i['category'] == 'Other'])
            },
            'ingredients': ingredient_list
        }, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print(f"\nOK Extracted {len(ingredient_list)} unique ingredients!")
    print(f"OK Saved to: {output_path}")
    
    print("\nCategory Breakdown:")
    categories = defaultdict(int)
    for ing in ingredient_list:
        categories[ing['category']] += 1
    
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} ingredients")
    
    print(f"\nMost Common Ingredients (used in 10+ recipes):")
    for ing in ingredient_list[:15]:
        if ing['usage_count'] >= 10:
            print(f"  - {ing['name']}: used in {ing['usage_count']} recipes")
    
    return ingredient_list

if __name__ == "__main__":
    print("\n" + "="*70)
    print("COMPREHENSIVE INGREDIENT DATABASE BUILDER")
    print("="*70 + "\n")
    
    ingredients = build_comprehensive_ingredient_database()
    
    print(f"\nOK Complete!")
    print(f"Your ingredient database now has {len(ingredients)} unique ingredients")
    print("\nNext: Update pp1_preparation.py to use the new comprehensive database")