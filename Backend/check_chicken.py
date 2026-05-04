import json
import os

path = r'cooking_assistant\rag\data\recipes_all_merged.json'

with open(path, 'r', encoding='utf-8') as f:
    recipes = json.load(f)

print(f"Total recipes: {len(recipes)}")
print()

# Find chicken recipes
chicken_recipes = []
for r in recipes:
    name = ''
    names = r.get('names', {})
    if isinstance(names, dict):
        name = names.get('english', '') or names.get('en', '')
    if not name:
        name = r.get('name', '')
    
    if 'chicken' in name.lower():
        chicken_recipes.append(r)

print(f"Recipes with 'chicken' in name: {len(chicken_recipes)}")
print()

if chicken_recipes:
    r = chicken_recipes[0]
    print(f"First chicken recipe: {r.get('names', r.get('name', ''))}")
    print(f"Keys in recipe: {list(r.keys())}")
    print()
    print("Ingredients sample:")
    for ing in r.get('ingredients', [])[:5]:
        print(f"  {ing}")
else:
    print("NO CHICKEN RECIPES FOUND IN DATABASE!")
    print()
    print("Sample recipe structure:")
    r = recipes[0]
    print(f"Keys: {list(r.keys())}")
    print(f"Name field: {r.get('name', r.get('names', 'NO NAME'))}")
    print(f"Ingredients sample:")
    for ing in r.get('ingredients', [])[:3]:
        print(f"  {ing}")