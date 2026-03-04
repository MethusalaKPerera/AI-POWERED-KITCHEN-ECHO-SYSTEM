"""
Meal Planner Backend Routes
Integrates with existing recipe database
"""
from flask import Blueprint, request, jsonify
import os
import json
import random
from collections import defaultdict

meal_planner_bp = Blueprint('meal_planner', __name__)

def _load_recipes():
    """Load recipes from merged database"""
    data_dir = os.path.join(os.path.dirname(__file__), 'rag', 'data')
    for fname in ['recipes_all_merged.json', 'new_200_recipes.json', 'recipe_database.json']:
        fp = os.path.join(data_dir, fname)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data.get('recipes', [])
            return data
    return []

@meal_planner_bp.route('/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    """Generate a weekly meal plan based on number of people and preferences"""
    try:
        data = request.json
        num_people = data.get('num_people', 1)
        preferences = data.get('preferences', {})
        
        recipes = _load_recipes()
        
        # Organize recipes by category
        by_category = defaultdict(list)
        for recipe in recipes:
            category = recipe.get('category', 'main dish').lower()
            by_category[category].append(recipe)
        
        # Create meal plan
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_plan = {}
        
        for day in days:
            meal_plan[day] = {
                'breakfast': _pick_recipe(by_category, 'breakfast'),
                'lunch': _pick_recipe(by_category, ['rice', 'rice dish', 'main dish']),
                'dinner': _pick_recipe(by_category, ['curry', 'main dish'])
            }
        
        return jsonify({
            'success': True,
            'meal_plan': meal_plan,
            'num_people': num_people
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@meal_planner_bp.route('/generate-grocery-list', methods=['POST'])
def generate_grocery_list():
    """Generate grocery list from meal plan"""
    try:
        data = request.json
        meal_plan = data.get('meal_plan', {})
        num_people = data.get('num_people', 1)
        
        recipes = _load_recipes()
        recipe_dict = {r.get('id') or r.get('name'): r for r in recipes}
        
        # Aggregate ingredients
        ingredient_totals = defaultdict(lambda: {'amount': 0, 'unit': 'g', 'category': 'other'})
        
        for day, meals in meal_plan.items():
            for meal_type, recipe_id in meals.items():
                recipe = recipe_dict.get(recipe_id)
                if recipe:
                    for ing in recipe.get('ingredients', []):
                        if isinstance(ing, dict):
                            name = ing.get('name', '')
                            amount = ing.get('amount', '')
                            # Simple aggregation logic
                            ingredient_totals[name]['amount'] += 1
                            ingredient_totals[name]['category'] = _categorize_ingredient(name)
        
        # Organize by category
        grocery_list = defaultdict(list)
        for ing_name, info in ingredient_totals.items():
            grocery_list[info['category']].append({
                'item': ing_name,
                'quantity': info['amount'] * num_people,
                'unit': info['unit']
            })
        
        return jsonify({
            'success': True,
            'grocery_list': dict(grocery_list),
            'num_people': num_people
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def _pick_recipe(by_category, categories):
    """Pick a random recipe from given categories"""
    if isinstance(categories, str):
        categories = [categories]
    
    for cat in categories:
        if cat in by_category and by_category[cat]:
            recipe = random.choice(by_category[cat])
            return recipe.get('id') or recipe.get('name')
    
    # Fallback to any recipe
    all_recipes = []
    for recipes in by_category.values():
        all_recipes.extend(recipes)
    if all_recipes:
        recipe = random.choice(all_recipes)
        return recipe.get('id') or recipe.get('name')
    return None

def _categorize_ingredient(name):
    """Categorize ingredient"""
    name_lower = name.lower()
    if any(x in name_lower for x in ['onion', 'tomato', 'potato', 'carrot', 'green', 'leaf', 'vegetable']):
        return 'vegetables'
    elif any(x in name_lower for x in ['chicken', 'fish', 'egg', 'meat', 'prawns']):
        return 'protein'
    elif any(x in name_lower for x in ['rice', 'flour', 'bread']):
        return 'grains'
    elif any(x in name_lower for x in ['curry', 'turmeric', 'cumin', 'chili', 'pepper', 'spice']):
        return 'spices'
    elif any(x in name_lower for x in ['milk', 'coconut milk', 'yogurt', 'cheese']):
        return 'dairy'
    return 'other'