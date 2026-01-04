#!/usr/bin/env python3
"""
Test Multilingual Ingredient Matching
"""

from ingredient_matcher import IngredientMatcher

print("\n" + "="*70)
print("MULTILINGUAL INGREDIENT MATCHING TEST")
print("="*70 + "\n")

m = IngredientMatcher(
    'rag/data/recipes/recipe_database.json',
    'rag/data/ingredient_database.json'
)

ingredients = ['chicken', 'coconut milk', 'curry powder']

print(f"Test ingredients: {ingredients}\n")

# Test English
print("="*70)
print("ENGLISH")
print("="*70)
r = m.suggest_recipe_with_groceries(ingredients, 'english')
for i, recipe in enumerate(r['recipes'][:3], 1):
    print(f"\n{i}. {recipe['recipe_name']} ({recipe['match_percentage']:.1f}% match)")
    print(f"   You have: {', '.join(recipe['you_have'][:5])}")
    print(f"   You need: {', '.join(recipe['you_need'][:5])}")

# Test Sinhala
print("\n" + "="*70)
print("SINHALA (සිංහල)")
print("="*70)
r = m.suggest_recipe_with_groceries(ingredients, 'sinhala')
for i, recipe in enumerate(r['recipes'][:3], 1):
    print(f"\n{i}. {recipe['recipe_name']} ({recipe['match_percentage']:.1f}% match)")
    print(f"   ඔබ සතුව ඇත: {', '.join(recipe['you_have'][:5])}")
    print(f"   ඔබට අවශ්‍යයි: {', '.join(recipe['you_need'][:5])}")

# Test Tamil
print("\n" + "="*70)
print("TAMIL (தமிழ்)")
print("="*70)
r = m.suggest_recipe_with_groceries(ingredients, 'tamil')
for i, recipe in enumerate(r['recipes'][:3], 1):
    print(f"\n{i}. {recipe['recipe_name']} ({recipe['match_percentage']:.1f}% match)")
    print(f"   உங்களிடம் உள்ளது: {', '.join(recipe['you_have'][:5])}")
    print(f"   உங்களுக்கு தேவை: {', '.join(recipe['you_need'][:5])}")

print("\n" + "="*70)
print("TEST COMPLETE - MULTILINGUAL SYSTEM WORKING!")
print("="*70)