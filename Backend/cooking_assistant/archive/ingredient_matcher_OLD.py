#!/usr/bin/env python3
"""
Ingredient-Based Recipe Matcher
Matches available ingredients with recipes and suggests what's needed
Supports English, Sinhala, and Tamil
For AI-Powered Kitchen Echo System
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

class IngredientMatcher:
    """Match ingredients to recipes and suggest missing items"""
    
    def __init__(self, recipe_db_path: str, ingredient_db_path: str):
        """Initialize with recipe and ingredient databases"""
        
        # Load recipe database
        with open(recipe_db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.recipes = data['recipes']
        
        # Load ingredient database
        with open(ingredient_db_path, 'r', encoding='utf-8') as f:
            self.ingredient_db = json.load(f)
        
        print(f"✅ Loaded {len(self.recipes)} recipes")
        print(f"✅ Loaded {self.ingredient_db['total_ingredients']} ingredients")
        
        # Create trilingual ingredient mapping
        self.create_multilingual_mapping()
    
    def create_multilingual_mapping(self):
        """Create mapping for ingredient names in all three languages"""
        
        # Common ingredient translations
        self.ingredient_translations = {
            'chicken': {'sinhala': 'කුකුල් මස්', 'tamil': 'கோழி', 'english': 'chicken'},
            'coconut': {'sinhala': 'පොල්', 'tamil': 'தேங்காய்', 'english': 'coconut'},
            'rice': {'sinhala': 'බත්', 'tamil': 'அரிசி', 'english': 'rice'},
            'curry': {'sinhala': 'කරිය', 'tamil': 'கறி', 'english': 'curry'},
            'onion': {'sinhala': 'ලූනු', 'tamil': 'வெங்காயம்', 'english': 'onion'},
            'garlic': {'sinhala': 'සුදු ලූනු', 'tamil': 'பூண்டு', 'english': 'garlic'},
            'chili': {'sinhala': 'මිරිස්', 'tamil': 'மிளகாய்', 'english': 'chili'},
            'salt': {'sinhala': 'ලුණු', 'tamil': 'உப்பு', 'english': 'salt'},
            'oil': {'sinhala': 'තෙල්', 'tamil': 'எண்ணெய்', 'english': 'oil'},
            'water': {'sinhala': 'වතුර', 'tamil': 'தண்ணீர்', 'english': 'water'},
            'lentils': {'sinhala': 'පරිප්පු', 'tamil': 'பருப்பு', 'english': 'lentils'},
            'milk': {'sinhala': 'කිරි', 'tamil': 'பால்', 'english': 'milk'},
            'fish': {'sinhala': 'මාලු', 'tamil': 'மீன்', 'english': 'fish'},
            'egg': {'sinhala': 'බිත්තර', 'tamil': 'முட்டை', 'english': 'egg'},
            'potato': {'sinhala': 'අල', 'tamil': 'உருளைக்கிழங்கு', 'english': 'potato'},
            'tomato': {'sinhala': 'තක්කාලි', 'tamil': 'தக்காளி', 'english': 'tomato'},
            'ginger': {'sinhala': 'ඉඟුරු', 'tamil': 'இஞ்சி', 'english': 'ginger'},
            'turmeric': {'sinhala': 'කහ', 'tamil': 'மஞ்சள்', 'english': 'turmeric'},
            'cinnamon': {'sinhala': 'කුරුඳු', 'tamil': 'பட்டை', 'english': 'cinnamon'},
            'cardamom': {'sinhala': 'එනසාල', 'tamil': 'ஏலக்காய்', 'english': 'cardamom'},
            'sugar': {'sinhala': 'සීනි', 'tamil': 'சர்க்கரை', 'english': 'sugar'}
        }
    
    def normalize_ingredient(self, ingredient: str) -> str:
        """Normalize ingredient name for matching"""
        return ingredient.lower().strip()
    
    def fuzzy_match(self, ing1: str, ing2: str, threshold: float = 0.7) -> bool:
        """Fuzzy match two ingredient names"""
        similarity = SequenceMatcher(None, ing1.lower(), ing2.lower()).ratio()
        return similarity >= threshold
    
    def find_matching_recipes(self, available_ingredients: List[str], 
                             min_match_percentage: float = 0.6) -> List[Dict]:
        """
        Find recipes that can be made with available ingredients
        
        Args:
            available_ingredients: List of ingredients user has
            min_match_percentage: Minimum percentage of ingredients needed to match
        
        Returns:
            List of matching recipes with match details
        """
        
        matches = []
        
        # Normalize available ingredients
        normalized_available = [self.normalize_ingredient(ing) for ing in available_ingredients]
        
        for recipe in self.recipes:
            # Extract main ingredients from recipe
            recipe_ingredients = []
            for ing in recipe['ingredients']:
                # Extract ingredient name (simplified)
                ing_name = self.extract_main_ingredient(ing)
                recipe_ingredients.append(ing_name)
            
            # Calculate match
            matched_ingredients = []
            missing_ingredients = []
            
            for recipe_ing in recipe_ingredients:
                found = False
                
                # Try exact and fuzzy matching
                for available_ing in normalized_available:
                    if (recipe_ing in available_ing or 
                        available_ing in recipe_ing or 
                        self.fuzzy_match(recipe_ing, available_ing)):
                        matched_ingredients.append(recipe_ing)
                        found = True
                        break
                
                if not found:
                    missing_ingredients.append(recipe_ing)
            
            # Calculate match percentage
            total_ingredients = len(recipe_ingredients)
            match_percentage = len(matched_ingredients) / total_ingredients if total_ingredients > 0 else 0
            
            # Add to matches if meets threshold
            if match_percentage >= min_match_percentage:
                match_info = {
                    'recipe': recipe,
                    'match_percentage': match_percentage,
                    'matched_ingredients': matched_ingredients,
                    'missing_ingredients': missing_ingredients,
                    'total_ingredients': total_ingredients,
                    'matched_count': len(matched_ingredients),
                    'missing_count': len(missing_ingredients)
                }
                matches.append(match_info)
        
        # Sort by match percentage (highest first)
        matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return matches
    
    def extract_main_ingredient(self, ingredient_text: str) -> str:
        """Extract main ingredient from full ingredient text"""
        import re
        
        # Remove measurements and common descriptors
        patterns_to_remove = [
            r'\d+\s*(?:kg|g|mg|l|ml|cup|cups|tbsp|tsp|teaspoon|tablespoon|pound|oz)',
            r'\d+/\d+',
            r'\d+',
            r'to taste',
            r'optional',
            r'finely\s+',
            r'chopped',
            r'diced',
            r'sliced',
            r'minced',
            r'cut into pieces',
            r'grated',
            r'fresh',
            r'dried'
        ]
        
        text = ingredient_text.lower()
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up
        text = text.strip(' ,-')
        
        # Get first significant word
        words = [w for w in text.split() if len(w) > 2]
        return words[0] if words else text
    
    def suggest_recipe_with_groceries(self, available_ingredients: List[str],
                                     language: str = 'english') -> Dict:
        """
        Suggest recipes and create grocery list for missing items
        
        Args:
            available_ingredients: What user has
            language: 'english', 'sinhala', or 'tamil'
        
        Returns:
            Dictionary with recipe suggestions and grocery list
        """
        
        # Find matching recipes
        matches = self.find_matching_recipes(available_ingredients, min_match_percentage=0.5)
        
        if not matches:
            return {
                'status': 'no_matches',
                'message': self.translate_message('No recipes found with those ingredients', language),
                'suggestions': []
            }
        
        # Take top 5 matches
        top_matches = matches[:5]
        
        suggestions = []
        
        for match in top_matches:
            recipe = match['recipe']
            
            # Get recipe name in requested language
            if language == 'sinhala':
                recipe_name = recipe.get('name_sinhala', recipe['name'])
            elif language == 'tamil':
                recipe_name = recipe.get('name_tamil', recipe['name'])
            else:
                recipe_name = recipe['name']
            
            # Create grocery list for missing items
            grocery_list = self.create_grocery_list(match['missing_ingredients'], language)
            
            suggestion = {
                'recipe_name': recipe_name,
                'recipe_name_english': recipe['name'],
                'recipe_id': recipe['id'],
                'match_percentage': round(match['match_percentage'] * 100, 1),
                'you_have': match['matched_ingredients'],
                'you_need': match['missing_ingredients'],
                'grocery_list': grocery_list,
                'difficulty': recipe['difficulty'],
                'prep_time': recipe['prep_time_minutes'],
                'cook_time': recipe['cook_time_minutes'],
                'servings': recipe['servings']
            }
            
            suggestions.append(suggestion)
        
        return {
            'status': 'success',
            'total_matches': len(matches),
            'showing_top': len(top_matches),
            'suggestions': suggestions
        }
    
    def create_grocery_list(self, missing_ingredients: List[str], 
                           language: str = 'english') -> List[Dict]:
        """Create grocery list with translations"""
        
        grocery_list = []
        
        for ingredient in missing_ingredients:
            # Try to find translation
            translation = self.get_ingredient_translation(ingredient, language)
            
            item = {
                'english': ingredient,
                'translated': translation,
                'category': self.categorize_ingredient(ingredient)
            }
            
            grocery_list.append(item)
        
        return grocery_list
    
    def get_ingredient_translation(self, ingredient: str, target_lang: str) -> str:
        """Get ingredient translation"""
        
        ingredient_lower = ingredient.lower()
        
        # Check if we have this in our translations
        for eng_name, translations in self.ingredient_translations.items():
            if eng_name in ingredient_lower:
                return translations.get(target_lang, ingredient)
        
        # If no translation found, return original
        return ingredient
    
    def categorize_ingredient(self, ingredient: str) -> str:
        """Categorize ingredient type"""
        
        categories = {
            'vegetables': ['onion', 'tomato', 'potato', 'carrot', 'cabbage'],
            'spices': ['curry', 'turmeric', 'chili', 'cinnamon', 'cardamom', 'cloves'],
            'proteins': ['chicken', 'fish', 'egg', 'lentils', 'dal'],
            'dairy': ['milk', 'yogurt', 'butter', 'ghee'],
            'staples': ['rice', 'flour', 'oil', 'salt', 'sugar']
        }
        
        ingredient_lower = ingredient.lower()
        
        for category, keywords in categories.items():
            if any(keyword in ingredient_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def translate_message(self, message: str, language: str) -> str:
        """Translate common messages"""
        
        messages = {
            'No recipes found with those ingredients': {
                'english': 'No recipes found with those ingredients',
                'sinhala': 'එම ද්‍රව්‍ය සමඟ කිසිදු වට්ටෝරුවක් හමු නොවීය',
                'tamil': 'அந்த பொருட்களுடன் எந்த சமையல் முறையும் காணவில்லை'
            }
        }
        
        return messages.get(message, {}).get(language, message)
    
    def format_result_for_display(self, result: Dict, language: str = 'english') -> str:
        """Format result in a readable way for display"""
        
        if result['status'] == 'no_matches':
            return result['message']
        
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"🍛 RECIPE SUGGESTIONS")
        output.append(f"   Found {result['total_matches']} matching recipes")
        output.append(f"{'='*70}\n")
        
        for i, suggestion in enumerate(result['suggestions'], 1):
            output.append(f"\n{i}. {suggestion['recipe_name']}")
            output.append(f"   Match: {suggestion['match_percentage']}%")
            output.append(f"   Difficulty: {suggestion['difficulty']}")
            output.append(f"   Time: {suggestion['prep_time']} + {suggestion['cook_time']} min")
            
            output.append(f"\n   ✅ You have ({len(suggestion['you_have'])}):")
            for ing in suggestion['you_have'][:5]:  # Show first 5
                output.append(f"      • {ing}")
            
            output.append(f"\n   🛒 You need ({len(suggestion['you_need'])}):")
            for item in suggestion['grocery_list'][:5]:  # Show first 5
                output.append(f"      • {item['translated']} ({item['category']})")
            
            output.append("")
        
        return '\n'.join(output)


def demo():
    """Demo the ingredient matcher"""
    
    print("\n" + "="*70)
    print("🍛 INGREDIENT-BASED RECIPE MATCHER - DEMO")
    print("="*70 + "\n")
    
    # Paths (adjust to your structure)
    recipe_db = 'Backend/cooking_assistant/rag/data/recipes/recipe_database.json'
    ingredient_db = 'Backend/cooking_assistant/rag/data/ingredient_database.json'
    
    try:
        matcher = IngredientMatcher(recipe_db, ingredient_db)
        
        # Example: User has these ingredients
        available = [
            'chicken',
            'coconut milk',
            'onion',
            'garlic',
            'curry powder',
            'oil',
            'salt'
        ]
        
        print(f"🥘 Available ingredients: {', '.join(available)}\n")
        
        # Find matches in English
        print("=" * 70)
        print("ENGLISH VERSION:")
        print("=" * 70)
        result_en = matcher.suggest_recipe_with_groceries(available, language='english')
        print(matcher.format_result_for_display(result_en, 'english'))
        
        # Find matches in Sinhala
        print("\n" + "=" * 70)
        print("SINHALA VERSION:")
        print("=" * 70)
        result_si = matcher.suggest_recipe_with_groceries(available, language='sinhala')
        print(matcher.format_result_for_display(result_si, 'sinhala'))
        
        # Find matches in Tamil
        print("\n" + "=" * 70)
        print("TAMIL VERSION:")
        print("=" * 70)
        result_ta = matcher.suggest_recipe_with_groceries(available, language='tamil')
        print(matcher.format_result_for_display(result_ta, 'tamil'))
        
    except FileNotFoundError as e:
        print(f"❌ Database files not found: {e}")
        print("\n💡 First run: integrated_recipe_collector.py")


if __name__ == "__main__":
    demo()