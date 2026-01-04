#!/usr/bin/env python3
"""
Diagnostic: Check what IngredientMatcher is actually doing
"""

from ingredient_matcher import IngredientMatcher
import json

print("="*70)
print("INGREDIENT MATCHER DIAGNOSTIC")
print("="*70)

# Initialize matcher
m = IngredientMatcher(
    'rag/data/recipes/recipe_database.json',
    'rag/data/ingredient_database.json'
)

print(f"\n1. Matcher initialized:")
print(f"   Recipes loaded: {len(m.recipes)}")
print(f"   Ingredient DB type: {type(m.ingredient_db)}")
print(f"   Ingredient DB length: {len(m.ingredient_db)}")

# Load first recipe to see actual ingredient format
with open('rag/data/recipes/recipe_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    first_recipe = data['recipes'][0]

print(f"\n2. First recipe in database:")
print(f"   Name: {first_recipe['name']}")
print(f"   Ingredients ({len(first_recipe['ingredients'])} total):")
for i, ing in enumerate(first_recipe['ingredients'][:5], 1):
    print(f"     {i}. {ing}")

# Test 1: Use exact ingredients from first recipe
print(f"\n3. TEST 1: Using EXACT ingredients from first recipe")
exact_ingredients = first_recipe['ingredients'][:4]  # First 4 ingredients
print(f"   Test ingredients: {exact_ingredients}")

result = m.suggest_recipe_with_groceries(exact_ingredients, 'english')
recipes = result.get('recipes', []) if isinstance(result, dict) else result

print(f"   Result: {len(recipes) if recipes else 0} matches found")
if recipes:
    for i, r in enumerate(recipes[:3], 1):
        print(f"     {i}. {r['recipe_name']}: {r['match_percentage']:.1f}%")

# Test 2: Use simple ingredient names
print(f"\n4. TEST 2: Using simple ingredient names")
simple_ingredients = ['chicken', 'coconut milk', 'curry powder']
print(f"   Test ingredients: {simple_ingredients}")

result2 = m.suggest_recipe_with_groceries(simple_ingredients, 'english')
recipes2 = result2.get('recipes', []) if isinstance(result2, dict) else result2

print(f"   Result: {len(recipes2) if recipes2 else 0} matches found")
if recipes2:
    for i, r in enumerate(recipes2[:3], 1):
        print(f"     {i}. {r['recipe_name']}: {r['match_percentage']:.1f}%")

# Test 3: Check what ingredients the matcher sees
print(f"\n5. Checking matcher's ingredient extraction:")
print(f"   Extracting ingredients from first recipe...")

# Manually check what the matcher extracts
if hasattr(m, 'extract_ingredients'):
    extracted = m.extract_ingredients(first_recipe['ingredients'])
    print(f"   Extracted: {extracted}")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)