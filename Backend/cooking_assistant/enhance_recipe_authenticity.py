#!/usr/bin/env python3
"""
Recipe Authenticity Enhancement Script
Enhances existing recipes with authentic Sri Lankan details
- Traditional cooking methods
- Authentic ingredient names
- Cultural context
- Regional variations
"""

import json
from pathlib import Path

# Enhancement rules for authentic Sri Lankan recipes
authenticity_enhancements = {
    "cooking_methods": {
        "use goraka not tamarind": "Goraka (dried garcinia) gives authentic sour taste",
        "coconut oil not vegetable oil": "Traditional Sri Lankan cooking uses coconut oil",
        "roasted curry powder": "Curry powder should be dry roasted first for depth",
        "Maldive fish": "Adds umami flavor - cannot substitute with anything else",
        "rampe and pandan": "Essential aromatics in Sri Lankan cooking",
        "curry leaves": "Must be fresh, not dried - integral to taste",
        "thick vs thin coconut milk": "First squeeze (thick) vs second squeeze (thin)",
    },
    
    "authentic_terms": {
        "treacle": "kithul treacle or coconut treacle - not maple syrup",
        "jaggery": "hakuru - palm jaggery, not white sugar",
        "goraka": "dried garcinia cambogia - unique to Sri Lanka",
        "Maldive fish": "umbalakada - dried tuna flakes",
        "rampe": "pandan leaf - for aroma",
        "curry leaves": "karapincha - not bay leaves",
        "lunu miris": "chili sambol made with onions and Maldive fish",
    }
}

def enhance_recipe_authenticity(recipe):
    """Add authentic details to a recipe"""
    
    enhanced = recipe.copy()
    name = recipe.get('name', '').lower()
    
    # Enhance based on recipe type
    if 'curry' in name:
        if not enhanced.get('cultural_notes'):
            enhanced['cultural_notes'] = ""
        
        # Add curry-specific authenticity notes
        if 'fish' in name or 'malu' in name:
            enhanced['cultural_notes'] += " Use fresh fish from coastal markets. Goraka (garcinia) is essential for authentic sour taste - never substitute with tamarind. The curry should have a deep red color from roasted spices."
        
        if 'chicken' in name or 'kukul' in name:
            enhanced['cultural_notes'] += " Roast curry powder in a dry pan first for authentic flavor. Use fresh curry leaves, not dried. Coconut milk should be added in two stages - thin first, thick at the end."
        
        if 'egg' in name or 'bittara' in name:
            enhanced['cultural_notes'] += " Hard-boil eggs and lightly fry them before adding to curry for better texture and color. This is the traditional village method."
    
    if 'sambol' in name:
        enhanced['cultural_notes'] = enhanced.get('cultural_notes', '') + " Must be freshly made - sambol loses flavor if stored too long. Maldive fish (umbalakada) is essential and irreplaceable. Use coconut scraped fresh, not desiccated."
    
    if 'rice' in name and 'milk' in name:
        enhanced['cultural_notes'] = enhanced.get('cultural_notes', '') + " Kiribath is served on all auspicious occasions. Must be eaten with lunu miris (chili sambol) and kithul treacle. Cut in diamond shapes for good luck."
    
    # Enhance ingredient notes
    ingredients = enhanced.get('ingredients', [])
    enhanced_ingredients = []
    
    for ing in ingredients:
        # Add notes to key ingredients
        if 'coconut oil' in ing.lower():
            enhanced_ingredients.append(ing + " (traditional - do not substitute)")
        elif 'curry leaves' in ing.lower():
            enhanced_ingredients.append(ing + " (fresh, not dried)")
        elif 'maldive fish' in ing.lower():
            enhanced_ingredients.append(ing + " (umbalakada - essential)")
        elif 'goraka' in ing.lower():
            enhanced_ingredients.append(ing + " (garcinia - cannot substitute)")
        elif 'treacle' in ing.lower() and 'kithul' not in ing.lower():
            enhanced_ingredients.append(ing.replace('treacle', 'kithul treacle'))
        elif 'jaggery' in ing.lower() and 'palm' not in ing.lower():
            enhanced_ingredients.append(ing.replace('jaggery', 'palm jaggery (hakuru)'))
        else:
            enhanced_ingredients.append(ing)
    
    enhanced['ingredients'] = enhanced_ingredients
    
    # Add authenticity tips to instructions
    instructions = enhanced.get('instructions', [])
    enhanced_instructions = []
    
    for step in instructions:
        step_lower = step.lower()
        
        # Enhance cooking methods
        if 'fry' in step_lower and 'curry' in step_lower and 'powder' in step_lower:
            enhanced_instructions.append(step + " (Fry until aromatic and oil separates - this is key to authentic flavor)")
        elif 'coconut milk' in step_lower and 'boil' in step_lower:
            enhanced_instructions.append(step.replace('boil', 'simmer gently') + " (Never boil coconut milk vigorously - it will curdle)")
        elif 'curry leaves' in step_lower:
            enhanced_instructions.append(step + " (Curry leaves must be fresh for authentic taste)")
        else:
            enhanced_instructions.append(step)
    
    enhanced['instructions'] = enhanced_instructions
    
    # Increase authenticity score if enhanced
    if enhanced != recipe:
        current_score = enhanced.get('authenticity_score', 85)
        enhanced['authenticity_score'] = min(100, current_score + 10)
    
    # Add region if missing
    if not enhanced.get('region'):
        enhanced['region'] = "General"
    
    # Add traditional cooking notes
    if 'tags' in enhanced:
        if 'traditional' not in enhanced['tags']:
            enhanced['tags'].append('traditional')
        if 'authentic' not in enhanced['tags']:
            enhanced['tags'].append('authentic')
    
    return enhanced

def enhance_all_recipes():
    """Enhance all recipes in the database"""
    
    print("\n" + "="*70)
    print("RECIPE AUTHENTICITY ENHANCEMENT")
    print("="*70 + "\n")
    
    # Load database
    db_path = Path('rag/data/recipes/recipe_database.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        recipes = data.get('recipes', [])
    
    print(f"📚 Found {len(recipes)} recipes to enhance\n")
    
    enhanced_count = 0
    enhanced_recipes = []
    
    for i, recipe in enumerate(recipes, 1):
        if i % 20 == 0:
            print(f"  Processing recipe {i}/{len(recipes)}...")
        
        original_score = recipe.get('authenticity_score', 85)
        enhanced = enhance_recipe_authenticity(recipe)
        new_score = enhanced.get('authenticity_score', 85)
        
        if new_score > original_score:
            enhanced_count += 1
            print(f"  ✅ Enhanced: {recipe['name']} ({original_score} → {new_score})")
        
        enhanced_recipes.append(enhanced)
    
    # Update database
    data['recipes'] = enhanced_recipes
    
    # Save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save individual files
    recipes_dir = Path('rag/data/recipes')
    for recipe in enhanced_recipes:
        recipe_file = recipes_dir / f"{recipe['id']}.json"
        with open(recipe_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "="*70)
    print("ENHANCEMENT COMPLETE")
    print("="*70)
    print(f"✅ Enhanced {enhanced_count} recipes")
    print(f"✅ Total recipes: {len(enhanced_recipes)}")
    print(f"✅ Saved to: {db_path}")
    
    # Show examples of enhancements
    print(f"\n📋 Example Enhancements:")
    print("-"*70)
    
    sample_enhanced = [r for r in enhanced_recipes if r.get('authenticity_score', 0) >= 95][:3]
    
    for recipe in sample_enhanced:
        print(f"\n{recipe['name']} (Score: {recipe['authenticity_score']})")
        print(f"  Region: {recipe.get('region', 'N/A')}")
        print(f"  Cultural Notes: {recipe.get('cultural_notes', 'N/A')[:100]}...")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Review enhanced recipes")
    print("2. Translate: python translate_with_deep_translator.py")
    print("3. Rebuild RAG: python recipe_rag_system.py")
    print("4. Update PP1: python pp1_preparation.py")
    print("="*70)

if __name__ == "__main__":
    enhance_all_recipes()
