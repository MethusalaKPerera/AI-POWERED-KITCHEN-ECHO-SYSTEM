#!/usr/bin/env python3
"""
Test Ingredient Matching System - FIXED VERSION
Shows how ingredient-based recipe recommendations work
"""

import json
from pathlib import Path
from ingredient_matcher import IngredientMatcher

def test_ingredient_matching():
    """Test ingredient matching with various scenarios"""
    
    print("\n" + "="*70)
    print("INGREDIENT MATCHING SYSTEM TEST")
    print("="*70 + "\n")
    
    # Initialize matcher
    matcher = IngredientMatcher(
        'rag/data/recipes/recipe_database.json',
        'rag/data/ingredient_database.json'
    )
    
    print(f"Loaded {len(matcher.recipes)} recipes")
    print(f"Loaded {len(matcher.ingredient_db)} ingredients\n")
    
    # Test scenarios
    test_cases = [
        {
            "name": "Test 1: Basic Curry Ingredients",
            "ingredients": ["chicken", "coconut milk", "onion", "curry powder"],
            "expected": "Chicken Curry"
        },
        {
            "name": "Test 2: Rice Dish",
            "ingredients": ["rice", "coconut", "cashews"],
            "expected": "Coconut Rice or Kiribath"
        },
        {
            "name": "Test 3: Sambol Ingredients",
            "ingredients": ["coconut", "chili", "onion", "lime"],
            "expected": "Pol Sambol"
        },
        {
            "name": "Test 4: Fish Curry",
            "ingredients": ["fish", "coconut milk", "curry powder"],
            "expected": "Fish Curry"
        },
        {
            "name": "Test 5: Dessert",
            "ingredients": ["coconut", "jaggery", "rice flour"],
            "expected": "Aluwa or Aggala"
        },
        {
            "name": "Test 6: Limited Ingredients",
            "ingredients": ["potato", "onion"],
            "expected": "Potato Curry"
        },
        {
            "name": "Test 7: Many Ingredients",
            "ingredients": ["chicken", "rice", "coconut milk", "curry powder", "onion", "garlic", "ginger"],
            "expected": "Chicken Biryani or Chicken Curry"
        }
    ]
    
    results_summary = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"{test['name']}")
        print(f"{'='*70}")
        print(f"Available ingredients: {', '.join(test['ingredients'])}")
        print(f"Expected recipe type: {test['expected']}\n")
        
        # Get recommendations
        result_dict = matcher.suggest_recipe_with_groceries(
            test['ingredients'],
            language='english'
        )
        
        # Extract recipe list from result dictionary
        recommendations = result_dict.get('recipes', []) if isinstance(result_dict, dict) else result_dict
        
        if recommendations and len(recommendations) > 0:
            print(f"Found {len(recommendations)} matching recipes:\n")
            
            for j, recipe in enumerate(recommendations[:5], 1):  # Show top 5
                match_pct = recipe['match_percentage']
                you_have = recipe['you_have']
                you_need = recipe['you_need']
                
                print(f"{j}. {recipe['recipe_name']}")
                print(f"   Match: {match_pct:.1f}% ({len(you_have)}/{len(you_have) + len(you_need)} ingredients)")
                print(f"   You have: {', '.join(you_have[:5])}")
                if you_need:
                    print(f"   You need: {', '.join(you_need[:5])}")
                    if len(you_need) > 5:
                        print(f"   ... and {len(you_need) - 5} more items")
                print()
                
            # Check if expected recipe is in top 3
            top_3_names = [r['recipe_name'].lower() for r in recommendations[:3]]
            expected_keywords = test['expected'].lower().split(' or ')
            
            found = any(
                any(keyword in name for keyword in expected_keywords)
                for name in top_3_names
            )
            
            results_summary.append({
                'test': test['name'],
                'found_expected': found,
                'top_match': recommendations[0]['recipe_name'],
                'match_pct': recommendations[0]['match_percentage']
            })
        else:
            print("⚠️ No matching recipes found!")
            results_summary.append({
                'test': test['name'],
                'found_expected': False,
                'top_match': None,
                'match_pct': 0
            })
    
    # Summary
    print("\n" + "="*70)
    print("ACCURACY SUMMARY")
    print("="*70 + "\n")
    
    correct = sum(1 for r in results_summary if r['found_expected'])
    total = len(results_summary)
    accuracy = (correct / total) * 100
    
    print(f"Total Tests: {total}")
    print(f"Expected Recipe Found in Top 3: {correct}")
    print(f"Accuracy: {accuracy:.1f}%\n")
    
    for result in results_summary:
        status = "✓" if result['found_expected'] else "✗"
        match_pct = f"{result['match_pct']:.1f}%" if result['match_pct'] > 0 else "N/A"
        print(f"{status} {result['test']}")
        if result['top_match']:
            print(f"  Top match: {result['top_match']} ({match_pct})")
        else:
            print(f"  No matches found")
    
    print("\n" + "="*70)
    print("MULTILINGUAL TEST")
    print("="*70 + "\n")
    
    # Test multilingual
    test_ingredients = ["chicken", "coconut milk", "curry powder"]
    
    print("Testing same ingredients in 3 languages:\n")
    print(f"Ingredients: {', '.join(test_ingredients)}\n")
    
    for lang in ['english', 'sinhala', 'tamil']:
        print(f"Language: {lang.upper()}")
        result_dict = matcher.suggest_recipe_with_groceries(
            test_ingredients,
            language=lang
        )
        
        # Extract recipe list
        results = result_dict.get('recipes', []) if isinstance(result_dict, dict) else result_dict
        
        if results and len(results) > 0:
            print(f"  Top match: {results[0]['recipe_name']} ({results[0]['match_percentage']:.1f}%)")
        else:
            print(f"  No matches found")
        print()
    
    print("="*70)
    print("TEST COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    test_ingredient_matching()