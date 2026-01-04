#!/usr/bin/env python3
"""
Ingredient Matcher - FIXED VERSION
Matches user ingredients with recipes and generates grocery lists
"""

import json
from pathlib import Path
from difflib import SequenceMatcher

class IngredientMatcher:
    def __init__(self, recipe_db_path, ingredient_db_path):
        """Initialize with recipe and ingredient databases"""
        
        # Load recipes
        with open(recipe_db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.recipes = data.get('recipes', [])
        
        # Load ingredient database
        with open(ingredient_db_path, 'r', encoding='utf-8') as f:
            ing_data = json.load(f)
            # Create dictionary for easy lookup
            self.ingredient_db = {}
            for ing in ing_data.get('ingredients', []):
                name = ing.get('name', '').lower()
                self.ingredient_db[name] = ing
        
        print(f"✅ Loaded {len(self.recipes)} recipes")
        print(f"✅ Loaded {len(self.ingredient_db)} ingredients")
    
    def extract_ingredient_name(self, ingredient_text):
        """Extract clean ingredient name from text like '500g chicken, cubed'"""
        import re
        
        text = ingredient_text.lower().strip()
        
        # Remove measurements with word boundaries
        measurements = r'\b(\d+\s*)?(kg|g|grams?|ml|l|liters?|cup|cups|tbsp|tablespoons?|tsp|teaspoons?|oz|ounces?|lb|pounds?|pieces?|inch|cm|mm)\b'
        text = re.sub(measurements, ' ', text)
        
        # Remove standalone numbers
        text = re.sub(r'\b\d+\s*', ' ', text)
        
        # Remove content in parentheses
        text = re.sub(r'\([^)]*\)', ' ', text)
        
        # Remove commas and everything after
        text = text.split(',')[0]
        
        # Clean up extra spaces
        text = ' '.join(text.split())
        
        # Remove common descriptors but keep the main ingredient
        descriptors = ['sliced', 'chopped', 'diced', 'minced', 'crushed', 
                      'grated', 'ground', 'fresh', 'dried', 'raw', 'cooked',
                      'boiled', 'fried', 'thick', 'thin', 'roasted']
        
        words = text.split()
        # Only remove descriptors, keep main ingredient words
        cleaned_words = [w for w in words if w not in descriptors and len(w) > 1]
        
        # Return cleaned ingredient name
        if len(cleaned_words) > 0:
            # Keep up to 3 words for compound ingredients
            return ' '.join(cleaned_words[:3])
        else:
            return text[:30]  # Fallback
    
    def fuzzy_match(self, str1, str2, threshold=0.6):
        """Check if two strings match with fuzzy logic"""
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        # Exact match
        if str1 == str2:
            return True
        
        # One contains the other
        if str1 in str2 or str2 in str1:
            return True
        
        # Fuzzy similarity
        ratio = SequenceMatcher(None, str1, str2).ratio()
        return ratio >= threshold
    
    def suggest_recipe_with_groceries(self, available_ingredients, language='english'):
        """
        Match recipes based on available ingredients
        Returns recipes with match percentage and grocery lists
        """
        
        # Normalize available ingredients
        normalized_available = []
        for ing in available_ingredients:
            clean = self.extract_ingredient_name(ing)
            normalized_available.append(clean)
        
        matching_recipes = []
        
        for recipe in self.recipes:
            recipe_ingredients = recipe.get('ingredients', [])
            
            # Extract ingredient names from recipe
            recipe_ing_names = []
            for ing in recipe_ingredients:
                clean = self.extract_ingredient_name(ing)
                recipe_ing_names.append(clean)
            
            # Count matches
            matched_ingredients = []
            needed_ingredients = []
            
            for recipe_ing in recipe_ing_names:
                found = False
                for available_ing in normalized_available:
                    if self.fuzzy_match(recipe_ing, available_ing, threshold=0.6):
                        matched_ingredients.append(recipe_ing)
                        found = True
                        break
                
                if not found:
                    needed_ingredients.append(recipe_ing)
            
            # Calculate match percentage
            total_ingredients = len(recipe_ing_names)
            if total_ingredients == 0:
                continue
            
            match_percentage = (len(matched_ingredients) / total_ingredients) * 100
            
            # Only include if at least some match
            if match_percentage > 0:
                # Get recipe name in requested language
                if language == 'sinhala':
                    recipe_name = recipe.get('name_sinhala', recipe.get('name', ''))
                elif language == 'tamil':
                    recipe_name = recipe.get('name_tamil', recipe.get('name', ''))
                else:
                    recipe_name = recipe.get('name', '')
                
                # Translate ingredient names if needed
                translated_you_have = self._translate_ingredients(matched_ingredients, language)
                translated_you_need = self._translate_ingredients(needed_ingredients, language)
                
                matching_recipes.append({
                    'recipe_id': recipe.get('id', ''),
                    'recipe_name': recipe_name,
                    'category': recipe.get('category', ''),
                    'match_percentage': match_percentage,
                    'you_have': translated_you_have,
                    'you_need': translated_you_need,
                    'total_ingredients': total_ingredients,
                    'difficulty': recipe.get('difficulty', ''),
                    'prep_time': recipe.get('prep_time_minutes', 0),
                    'cook_time': recipe.get('cook_time_minutes', 0)
                })
        
        # Sort by match percentage (highest first)
        matching_recipes.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return {
            'total_matches': len(matching_recipes),
            'recipes': matching_recipes,
            'language': language
        }
    
    def _translate_ingredients(self, ingredient_list, language):
        """Translate ingredient names based on language"""
        if language == 'english':
            return ingredient_list
        
        translated = []
        for ing_name in ingredient_list:
            # Look up in ingredient database
            ing_lower = ing_name.lower()
            if ing_lower in self.ingredient_db:
                ing_data = self.ingredient_db[ing_lower]
                if language == 'sinhala' and ing_data.get('name_sinhala'):
                    translated.append(ing_data['name_sinhala'])
                elif language == 'tamil' and ing_data.get('name_tamil'):
                    translated.append(ing_data['name_tamil'])
                else:
                    translated.append(ing_name)  # Fallback to English
            else:
                translated.append(ing_name)  # Not in database
        
        return translated

if __name__ == "__main__":
    # Test the matcher
    print("\n" + "="*70)
    print("INGREDIENT MATCHER TEST")
    print("="*70 + "\n")
    
    matcher = IngredientMatcher(
        'rag/data/recipes/recipe_database.json',
        'rag/data/ingredient_database.json'
    )
    
    # Test with simple ingredients
    test_ingredients = ['chicken', 'coconut milk', 'onion', 'curry powder']
    print(f"Testing with: {test_ingredients}\n")
    
    result = matcher.suggest_recipe_with_groceries(test_ingredients, 'english')
    
    print(f"Found {result['total_matches']} matching recipes!\n")
    
    for i, recipe in enumerate(result['recipes'][:5], 1):
        print(f"{i}. {recipe['recipe_name']}")
        print(f"   Match: {recipe['match_percentage']:.1f}%")
        print(f"   You have ({len(recipe['you_have'])}): {', '.join(recipe['you_have'][:3])}")
        if len(recipe['you_have']) > 3:
            print(f"      ... and {len(recipe['you_have']) - 3} more")
        print(f"   You need ({len(recipe['you_need'])}): {', '.join(recipe['you_need'][:3])}")
        if len(recipe['you_need']) > 3:
            print(f"      ... and {len(recipe['you_need']) - 3} more")
        print()