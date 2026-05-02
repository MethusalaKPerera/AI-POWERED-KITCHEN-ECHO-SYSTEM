#!/usr/bin/env python3
"""
Integrated Recipe Dataset Builder for AI-Powered Kitchen Echo System
Collects recipes from web + PDFs and saves in your project structure
Creates trilingual recipes (English, Sinhala, Tamil) for RAG system
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Add your project path
sys.path.append('Backend/cooking_assistant')

# Configuration for your project structure
# These paths are relative to the cooking_assistant folder (where this script is)
PROJECT_BASE = Path('.')  # Current directory (cooking_assistant)
RAG_DATA_PATH = PROJECT_BASE / 'rag' / 'data'
RECIPES_PATH = RAG_DATA_PATH / 'recipes'
SRI_LANKAN_RECIPES_PATH = PROJECT_BASE / 'data' / 'sri_lankan_recipes'

class IntegratedRecipeCollector:
    """Collects and organizes recipes for your RAG system"""
    
    def __init__(self):
        self.recipes = []
        self.recipe_counter = 1
        
        # Create directories if they don't exist
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            RECIPES_PATH,
            SRI_LANKAN_RECIPES_PATH,
            RAG_DATA_PATH / 'embeddings',
            RAG_DATA_PATH / 'processed',
            PROJECT_BASE / 'data' / 'extracted',
            PROJECT_BASE / 'data' / 'raw_pdfs'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created/verified: {directory}")
    
    def create_sample_recipes(self):
        """Create sample authentic Sri Lankan recipes for quick testing"""
        
        sample_recipes = [
            {
                "id": "recipe_001",
                "name": "Chicken Curry (Kukul Mas Curry)",
                "name_sinhala": "කුකුල් මස් කරිය",
                "name_tamil": "கோழி கறி",
                "category": "Curry",
                "region": "Sinhalese",
                "description": "A rich, aromatic chicken curry with roasted Sri Lankan spices and coconut milk",
                "ingredients": [
                    "1 kg chicken, cut into pieces",
                    "400ml thick coconut milk",
                    "200ml thin coconut milk",
                    "3 tbsp roasted curry powder",
                    "1 tbsp chili powder",
                    "1 tsp turmeric powder",
                    "2 large onions, sliced",
                    "4 cloves garlic, minced",
                    "1 inch ginger, minced",
                    "2-3 green chilies",
                    "1 sprig curry leaves",
                    "1 stick cinnamon",
                    "3 cardamom pods",
                    "4 cloves",
                    "2 tbsp vegetable oil",
                    "Salt to taste"
                ],
                "instructions": [
                    "Marinate chicken with turmeric, chili powder, and salt for 30 minutes",
                    "Heat oil in a large pan and add cinnamon, cardamom, and cloves",
                    "Add curry leaves and sauté until fragrant",
                    "Add sliced onions and cook until golden brown",
                    "Add garlic, ginger, and green chilies; sauté for 2 minutes",
                    "Add roasted curry powder and cook for 1 minute",
                    "Add marinated chicken and mix well",
                    "Pour in thin coconut milk and bring to a boil",
                    "Reduce heat and simmer for 30 minutes until chicken is tender",
                    "Add thick coconut milk and simmer for 10 more minutes",
                    "Adjust seasoning and serve hot with rice"
                ],
                "prep_time_minutes": 30,
                "cook_time_minutes": 45,
                "servings": 6,
                "difficulty": "Medium",
                "tags": ["spicy", "coconut-based", "main-dish", "traditional"],
                "cultural_notes": "This is the most popular Sri Lankan chicken curry, typically served at special occasions and family gatherings",
                "tips": {
                    "sinhala": ["ඉඟුරු ගෙඩිය කැබලි කර යුෂ ගමුකර ඇටකිරි වලින් රස වැඩි වේ"],
                    "tamil": ["சமையலுக்கு முன் கோழியை மசாலாவில் ஊறவைக்கவும்"],
                    "english": ["Use freshly roasted curry powder for best flavor", "Marinating overnight enhances the taste"]
                },
                "authenticity_score": 0.95,
                "source": "Traditional Sri Lankan recipe"
            },
            {
                "id": "recipe_002",
                "name": "Dhal Curry (Parippu Curry)",
                "name_sinhala": "පරිප්පු කරිය",
                "name_tamil": "பருப்பு கறி",
                "category": "Curry",
                "region": "General",
                "description": "Creamy red lentil curry with coconut milk and tempered spices",
                "ingredients": [
                    "1 cup red lentils (masoor dal)",
                    "200ml coconut milk",
                    "2 cups water",
                    "1 tsp turmeric powder",
                    "1 tsp chili powder",
                    "1 large onion, diced",
                    "2 cloves garlic, minced",
                    "1 sprig curry leaves",
                    "1 tsp mustard seeds",
                    "1 tsp cumin seeds",
                    "2 green chilies",
                    "2 tbsp oil",
                    "Salt to taste"
                ],
                "instructions": [
                    "Wash lentils thoroughly and drain",
                    "In a pot, combine lentils, water, turmeric, and salt",
                    "Bring to a boil and simmer for 20 minutes until lentils are soft",
                    "Add coconut milk and chili powder; simmer for 5 minutes",
                    "For tempering: heat oil in a small pan",
                    "Add mustard seeds and cumin; let them splutter",
                    "Add curry leaves, onions, garlic, and green chilies",
                    "Sauté until onions are golden",
                    "Pour tempering over the dhal curry",
                    "Mix well and serve hot"
                ],
                "prep_time_minutes": 10,
                "cook_time_minutes": 25,
                "servings": 4,
                "difficulty": "Easy",
                "tags": ["vegetarian", "protein-rich", "everyday", "coconut-based"],
                "cultural_notes": "Dhal curry is a staple in Sri Lankan cuisine, eaten daily with rice",
                "tips": {
                    "sinhala": ["පරිප්පු මදි වැඩියෙන් තම්බා රස අඩු වේ"],
                    "tamil": ["பருப்பை நன்கு வேகவிடவும்"],
                    "english": ["Don't overcook lentils or they'll become mushy", "Adjust consistency with water"]
                },
                "authenticity_score": 0.98,
                "source": "Traditional Sri Lankan recipe"
            },
            {
                "id": "recipe_003",
                "name": "Coconut Sambol (Pol Sambol)",
                "name_sinhala": "පොල් සම්බෝල",
                "name_tamil": "தேங்காய் சம்பல்",
                "category": "Sambol",
                "region": "General",
                "description": "Spicy coconut condiment with chili, onions, and lime",
                "ingredients": [
                    "2 cups freshly grated coconut",
                    "1 large onion, finely chopped",
                    "2 tbsp chili powder (or to taste)",
                    "1 tsp salt",
                    "2 tbsp lime juice",
                    "1 tsp Maldive fish (optional)",
                    "Few curry leaves, chopped"
                ],
                "instructions": [
                    "In a large bowl, combine grated coconut and salt",
                    "Add chili powder and mix well",
                    "Add finely chopped onions",
                    "Add Maldive fish if using",
                    "Add chopped curry leaves",
                    "Squeeze lime juice over the mixture",
                    "Mix everything thoroughly with your hands",
                    "Adjust seasoning to taste",
                    "Serve immediately or store in refrigerator"
                ],
                "prep_time_minutes": 15,
                "cook_time_minutes": 0,
                "servings": 6,
                "difficulty": "Easy",
                "tags": ["condiment", "spicy", "no-cook", "traditional"],
                "cultural_notes": "Pol sambol is the most essential Sri Lankan condiment, served with every meal",
                "tips": {
                    "sinhala": ["අත්තම පොල් ගාලා හැදුවොත් රස වැඩි"],
                    "tamil": ["புதிய தேங்காய் பயன்படுத்தவும்"],
                    "english": ["Use fresh coconut for best taste", "Can be stored for 2-3 days refrigerated"]
                },
                "authenticity_score": 1.0,
                "source": "Traditional Sri Lankan recipe"
            }
        ]
        
        return sample_recipes
    
    def save_to_project_structure(self, recipes):
        """Save recipes in your existing project structure"""
        
        # 1. Save main recipe JSON file
        main_recipe_file = RECIPES_PATH / 'recipe_database.json'
        with open(main_recipe_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_recipes': len(recipes),
                'created_date': datetime.now().isoformat(),
                'recipes': recipes
            }, f, indent=2, ensure_ascii=False)
        
        print(f"OK Saved main database: {main_recipe_file}")
        
        # 2. Save individual recipe JSON files (like your existing structure)
        for recipe in recipes:
            recipe_file = RECIPES_PATH / f"{recipe['id']}.json"
            with open(recipe_file, 'w', encoding='utf-8') as f:
                json.dump(recipe, f, indent=2, ensure_ascii=False)
        
        print(f"OK Saved {len(recipes)} individual recipe files")
        
        # 3. Save text files in sri_lankan_recipes folder
        for recipe in recipes:
            # Create a readable text version
            txt_filename = f"{recipe['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}.txt"
            txt_file = SRI_LANKAN_RECIPES_PATH / txt_filename
            
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"{'='*70}\n")
                f.write(f"{recipe['name']}\n")
                f.write(f"{recipe.get('name_sinhala', '')}\n")
                f.write(f"{recipe.get('name_tamil', '')}\n")
                f.write(f"{'='*70}\n\n")
                
                f.write(f"Category: {recipe['category']}\n")
                f.write(f"Region: {recipe.get('region', 'General')}\n")
                f.write(f"Difficulty: {recipe['difficulty']}\n")
                f.write(f"Prep Time: {recipe['prep_time_minutes']} minutes\n")
                f.write(f"Cook Time: {recipe['cook_time_minutes']} minutes\n")
                f.write(f"Servings: {recipe['servings']}\n\n")
                
                f.write(f"Description:\n{recipe['description']}\n\n")
                
                f.write("INGREDIENTS:\n")
                f.write("-" * 40 + "\n")
                for ing in recipe['ingredients']:
                    f.write(f"• {ing}\n")
                f.write("\n")
                
                f.write("INSTRUCTIONS:\n")
                f.write("-" * 40 + "\n")
                for i, step in enumerate(recipe['instructions'], 1):
                    f.write(f"{i}. {step}\n")
                f.write("\n")
                
                if recipe.get('cultural_notes'):
                    f.write(f"Cultural Notes:\n{recipe['cultural_notes']}\n\n")
                
                if recipe.get('tips'):
                    f.write("TIPS:\n")
                    for tip in recipe['tips'].get('english', []):
                        f.write(f"• {tip}\n")
        
        print(f"OK Saved text files to: {SRI_LANKAN_RECIPES_PATH}")
        
        # 4. Create ingredient database for matching
        self.create_ingredient_database(recipes)
        
        return main_recipe_file
    
    def create_ingredient_database(self, recipes):
        """Create a searchable ingredient database"""
        
        all_ingredients = set()
        ingredient_to_recipes = {}
        
        for recipe in recipes:
            recipe_id = recipe['id']
            recipe_name = recipe['name']
            
            for ingredient in recipe['ingredients']:
                # Extract main ingredient name (remove measurements)
                ingredient_clean = self.extract_ingredient_name(ingredient)
                all_ingredients.add(ingredient_clean)
                
                if ingredient_clean not in ingredient_to_recipes:
                    ingredient_to_recipes[ingredient_clean] = []
                
                ingredient_to_recipes[ingredient_clean].append({
                    'recipe_id': recipe_id,
                    'recipe_name': recipe_name,
                    'full_ingredient': ingredient
                })
        
        ingredient_db = {
            'total_ingredients': len(all_ingredients),
            'ingredients': sorted(list(all_ingredients)),
            'ingredient_to_recipes': ingredient_to_recipes
        }
        
        ingredient_file = RAG_DATA_PATH / 'ingredient_database.json'
        with open(ingredient_file, 'w', encoding='utf-8') as f:
            json.dump(ingredient_db, f, indent=2, ensure_ascii=False)
        
        print(f"OK Created ingredient database: {ingredient_file}")
        print(f"   Total unique ingredients: {len(all_ingredients)}")
    
    def extract_ingredient_name(self, ingredient_text):
        """Extract main ingredient name from full text"""
        import re
        
        # Remove common measurements
        measurements = [
            r'\d+\s*(?:kg|g|mg|l|ml|cup|cups|tbsp|tsp|teaspoon|tablespoon|pound|oz)',
            r'\d+/\d+',
            r'\d+',
            r'to taste',
            r'optional',
            r'finely chopped',
            r'diced',
            r'sliced',
            r'minced',
            r'cut into pieces',
            r'grated'
        ]
        
        text = ingredient_text.lower()
        for pattern in measurements:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up
        text = text.strip(' ,-')
        
        # Get main ingredient (first significant word)
        words = text.split()
        if words:
            return words[0] if len(words[0]) > 2 else ' '.join(words[:2])
        
        return text
    
    def generate_stats(self, recipes):
        """Generate statistics for your PP1 presentation"""
        
        categories = {}
        total_ingredients = set()
        
        for recipe in recipes:
            cat = recipe.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + 1
            
            for ing in recipe['ingredients']:
                total_ingredients.add(self.extract_ingredient_name(ing))
        
        stats = {
            'total_recipes': len(recipes),
            'categories': categories,
            'total_unique_ingredients': len(total_ingredients),
            'average_prep_time': sum(r['prep_time_minutes'] for r in recipes) / len(recipes),
            'average_cook_time': sum(r['cook_time_minutes'] for r in recipes) / len(recipes),
            'trilingual_support': True,
            'authenticity_scores': {
                'high': len([r for r in recipes if r.get('authenticity_score', 0) >= 0.9]),
                'medium': len([r for r in recipes if 0.7 <= r.get('authenticity_score', 0) < 0.9]),
                'low': len([r for r in recipes if r.get('authenticity_score', 0) < 0.7])
            }
        }
        
        stats_file = RAG_DATA_PATH / 'dataset_statistics.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*70)
        print("STATS DATASET STATISTICS")
        print("="*70)
        print(f"Total Recipes: {stats['total_recipes']}")
        print(f"Categories: {dict(categories)}")
        print(f"Unique Ingredients: {stats['total_unique_ingredients']}")
        print(f"Avg Prep Time: {stats['average_prep_time']:.1f} minutes")
        print(f"Avg Cook Time: {stats['average_cook_time']:.1f} minutes")
        print(f"High Authenticity Recipes: {stats['authenticity_scores']['high']}")
        print("="*70 + "\n")
        
        return stats


def main():
    """Main execution"""
    
    print("\n" + "="*70)
    print("INTEGRATED RECIPE DATASET BUILDER")
    print("   For AI-Powered Kitchen Echo System")
    print("="*70 + "\n")
    
    collector = IntegratedRecipeCollector()
    
    # Create sample recipes
    print("NOTE Creating sample Sri Lankan recipes...")
    recipes = collector.create_sample_recipes()
    
    # Save to your project structure
    print("\n Saving to project structure...")
    collector.save_to_project_structure(recipes)
    
    # Generate statistics
    print("\nSTATS Generating statistics...")
    collector.generate_stats(recipes)
    
    print("\nOK COMPLETE!")
    print(f"📁 Recipes saved in: {RECIPES_PATH}")
    print(f"📁 Text files in: {SRI_LANKAN_RECIPES_PATH}")
    print(f"📁 RAG data in: {RAG_DATA_PATH}")
    
    print("\n🔜 NEXT STEPS:")
    print("1. Run web extraction to add 150+ more recipes")
    print("2. Process recipes for RAG embeddings")
    print("3. Test ingredient matching system")
    print("4. Build frontend demo")


if __name__ == "__main__":
    main()