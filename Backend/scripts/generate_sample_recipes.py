#!/usr/bin/env python3
"""
Generate sample recipe data for testing
Run this to populate your recipe files with sample data
"""

import json
from pathlib import Path

# Sample recipes database
SAMPLE_RECIPES = [
    {
        "id": "001", "name": "Classic Spaghetti Carbonara", "cuisine": "Italian", "meal_type": "Dinner",
        "difficulty": "Medium", "prep_time": 10, "cook_time": 20, "servings": 4,
        "ingredients": ["400g spaghetti", "200g pancetta", "4 eggs", "100g Parmesan", "Salt", "Black pepper"],
        "instructions": ["Boil pasta", "Fry pancetta", "Mix eggs with cheese", "Combine all", "Serve hot"],
        "nutritional_info": {"calories": 520, "protein": "28g", "carbs": "65g", "fat": "18g"},
        "tags": ["pasta", "italian"], "dietary_restrictions": [], "allergens": ["eggs", "dairy", "gluten"]
    },
    {
        "id": "002", "name": "Chicken Fried Rice", "cuisine": "Chinese", "meal_type": "Lunch",
        "difficulty": "Easy", "prep_time": 15, "cook_time": 15, "servings": 4,
        "ingredients": ["3 cups rice", "2 chicken breasts", "3 eggs", "Soy sauce", "Vegetables", "Garlic"],
        "instructions": ["Cook rice", "Stir-fry chicken", "Scramble eggs", "Mix all together", "Add soy sauce"],
        "nutritional_info": {"calories": 450, "protein": "25g", "carbs": "55g", "fat": "12g"},
        "tags": ["rice", "chinese", "stir-fry"], "dietary_restrictions": [], "allergens": ["eggs", "soy"]
    },
    {
        "id": "003", "name": "Margherita Pizza", "cuisine": "Italian", "meal_type": "Dinner",
        "difficulty": "Medium", "prep_time": 30, "cook_time": 15, "servings": 2,
        "ingredients": ["Pizza dough", "Tomato sauce", "Mozzarella", "Fresh basil", "Olive oil"],
        "instructions": ["Roll dough", "Spread sauce", "Add cheese", "Bake at 220°C", "Top with basil"],
        "nutritional_info": {"calories": 680, "protein": "24g", "carbs": "72g", "fat": "28g"},
        "tags": ["pizza", "italian", "vegetarian"], "dietary_restrictions": ["vegetarian"], "allergens": ["gluten", "dairy"]
    },
    {
        "id": "004", "name": "Caesar Salad", "cuisine": "American", "meal_type": "Lunch",
        "difficulty": "Easy", "prep_time": 15, "cook_time": 0, "servings": 2,
        "ingredients": ["Romaine lettuce", "Croutons", "Parmesan", "Caesar dressing", "Lemon"],
        "instructions": ["Wash lettuce", "Mix with dressing", "Add croutons", "Top with cheese", "Serve"],
        "nutritional_info": {"calories": 320, "protein": "12g", "carbs": "18g", "fat": "22g"},
        "tags": ["salad", "healthy", "quick"], "dietary_restrictions": ["vegetarian"], "allergens": ["dairy", "gluten"]
    },
    {
        "id": "005", "name": "Beef Tacos", "cuisine": "Mexican", "meal_type": "Dinner",
        "difficulty": "Easy", "prep_time": 10, "cook_time": 20, "servings": 4,
        "ingredients": ["500g ground beef", "Taco shells", "Lettuce", "Tomatoes", "Cheese", "Salsa"],
        "instructions": ["Brown beef", "Season with spices", "Warm taco shells", "Assemble tacos", "Serve with toppings"],
        "nutritional_info": {"calories": 420, "protein": "28g", "carbs": "32g", "fat": "20g"},
        "tags": ["tacos", "mexican", "quick"], "dietary_restrictions": [], "allergens": ["dairy", "gluten"]
    }
]

def generate_sample_recipes(num_recipes=50):
    """Generate sample recipe files"""
    recipe_dir = Path("cooking_assistant/rag/data/recipes")
    recipe_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Generating {num_recipes} sample recipes...")
    
    # Use the 5 base recipes and create variations
    for i in range(1, num_recipes + 1):
        # Pick a base recipe (cycle through the 5)
        base_recipe = SAMPLE_RECIPES[(i - 1) % len(SAMPLE_RECIPES)].copy()
        
        # Modify the recipe
        recipe = {
            "id": f"{i:03d}",
            "name": f"{base_recipe['name']} (Variation {i})" if i > 5 else base_recipe['name'],
            "cuisine": base_recipe['cuisine'],
            "meal_type": base_recipe['meal_type'],
            "difficulty": base_recipe['difficulty'],
            "prep_time": base_recipe['prep_time'],
            "cook_time": base_recipe['cook_time'],
            "servings": base_recipe['servings'],
            "ingredients": base_recipe['ingredients'],
            "instructions": base_recipe['instructions'],
            "nutritional_info": base_recipe['nutritional_info'],
            "tags": base_recipe['tags'],
            "dietary_restrictions": base_recipe.get('dietary_restrictions', []),
            "allergens": base_recipe.get('allergens', []),
            "image_url": f"recipe_{i:03d}.jpg"
        }
        
        # Save recipe
        recipe_path = recipe_dir / f"recipe_{i:03d}.json"
        with open(recipe_path, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created {num_recipes} recipe files!")
    print(f"📁 Location: {recipe_dir.absolute()}")
    print("\n💡 Tip: Edit these files to add your own recipes!")

def main():
    print("="*60)
    print("🍳 SAMPLE RECIPE GENERATOR")
    print("="*60)
    
    choice = input("\nHow many recipes do you want to generate? (default: 50): ").strip()
    
    try:
        num_recipes = int(choice) if choice else 50
    except ValueError:
        print("Invalid input. Using default: 50")
        num_recipes = 50
    
    generate_sample_recipes(num_recipes)
    
    print("\n" + "="*60)
    print("✅ DONE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python scripts/setup_rag.py")
    print("2. Run: python scripts/test_rag.py")
    print("3. Edit recipe files with your actual recipes")

if __name__ == "__main__":
    main()