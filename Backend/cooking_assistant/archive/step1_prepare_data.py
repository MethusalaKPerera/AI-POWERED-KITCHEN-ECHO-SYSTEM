"""
STEP 1 — PREPARE DATA
=====================
Run this first to check your recipe files are being read correctly.

Place this file in:
  Backend/cooking_assistant/

Then run:
  cd Backend/cooking_assistant
  python step1_prepare_data.py
"""

import json
import os

# ── Category mapping ───────────────────────────────────────────────────────────
# Maps keywords found in recipe category/name → one of 7 standard categories
CATEGORY_MAP = {
    'curry':     0,
    'rice':      1,
    'breakfast': 2,
    'snack':     3,
    'festival':  4,
    'dessert':   5,
    'beverage':  6,
}

CATEGORY_NAMES = {v: k.title() for k, v in CATEGORY_MAP.items()}

# Rules for guessing category from recipe name/category field
CATEGORY_KEYWORDS = {
    0: ['curry', 'kari', 'mas', 'malu', 'kulambu', 'sothi', 'kozhi'],
    1: ['rice', 'bath', 'sadam', 'biryani', 'fried rice', 'kiribath', 'congee'],
    2: ['breakfast', 'hopper', 'appam', 'pittu', 'idiyappam', 'string hopper',
        'roti', 'pol roti', 'kottu', 'dosa', 'idli', 'upma', 'string'],
    3: ['snack', 'cutlet', 'roll', 'wade', 'vade', 'murukku', 'mixture',
        'samosa', 'pani', 'acharu', 'isso', 'bites', 'short eats'],
    4: ['festival', 'kavum', 'kokis', 'athirasa', 'aluwa', 'pani walalu',
        'halapa', 'thala', 'traditional', 'kiribath'],
    5: ['dessert', 'pudding', 'watalappan', 'wattalapam', 'cake', 'sweet',
        'halwa', 'payasam', 'kheer', 'paal', 'ice cream', 'ladoo'],
    6: ['beverage', 'drink', 'juice', 'tea', 'coffee', 'lassi', 'king coconut',
        'faluda', 'thambili'],
}


def guess_category(recipe):
    """Guess category label from recipe data."""
    # Try explicit category field first
    cat_field = recipe.get('category', '').lower().strip()
    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in cat_field for kw in keywords):
            return cat_id

    # Try from recipe name
    name = ''
    names = recipe.get('names', {})
    if isinstance(names, dict):
        name = names.get('english', '') or names.get('en', '')
    name = name or recipe.get('name', '')
    name = name.lower()

    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name for kw in keywords):
            return cat_id

    # Default to curry (most common Sri Lankan recipe type)
    return 0


def build_recipe_text(recipe):
    """
    Convert a recipe dict into a single text string for Sentence-BERT.
    
    Example output:
    "Chicken Curry. Category: curry. Ingredients: chicken pieces,
     onion, tomato, coconut milk, curry powder, turmeric."
    """
    # Get name
    names = recipe.get('names', {})
    if isinstance(names, dict):
        name = names.get('english', '') or names.get('en', '')
    else:
        name = str(names) if names else ''
    name = name or recipe.get('name', 'Unknown Recipe')

    # Get ingredients
    ing_list = []
    for ing in recipe.get('ingredients', []):
        if isinstance(ing, dict):
            ing_name = ing.get('name', '')
            if isinstance(ing_name, dict):
                ing_name = ing_name.get('english', '')
        else:
            ing_name = str(ing)

        # Strip numeric prefixes like "500g" or "2 tbsp"
        import re
        ing_name = re.sub(r'^\d+[\d./]*\s*(g|kg|ml|l|cup|tsp|tbsp|oz|lb|piece|pieces)?\s*', '', 
                          ing_name.strip(), flags=re.IGNORECASE)
        if ing_name.strip():
            ing_list.append(ing_name.strip().lower())

    # Get category label
    cat_field = recipe.get('category', '')
    
    # Build text
    text_parts = [name]
    if cat_field:
        text_parts.append(f"Category: {cat_field}")
    if ing_list:
        text_parts.append(f"Ingredients: {', '.join(ing_list)}")

    # Add instructions snippet if available (adds semantic richness)
    instructions = recipe.get('instructions', '') or recipe.get('method', '')
    if instructions and isinstance(instructions, str) and len(instructions) > 20:
        # Just first 100 chars to add context without dominating
        text_parts.append(instructions[:100])

    return '. '.join(text_parts)


def load_recipes():
    """Load recipes from your JSON files — tries all known locations."""
    # Try: same directory as this script
    base = os.path.dirname(os.path.abspath(__file__))
    
    candidates = [
        os.path.join(base, 'rag', 'data', 'recipes_all_merged.json'),
        os.path.join(base, 'rag', 'data', 'new_200_recipes.json'),
        os.path.join(base, 'rag', 'data', 'recipe_database.json'),
        os.path.join(base, '..', 'scripts', 'generate_recipes_data_p1.json'),
    ]

    for fp in candidates:
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            recipes = data.get('recipes', []) if isinstance(data, dict) else data
            if recipes:
                print(f"[✓] Loaded {len(recipes)} recipes from: {os.path.basename(fp)}")
                return recipes

    # Try loading multiple p1..p9 files from scripts/
    recipes = []
    scripts_dir = os.path.join(base, '..', 'scripts')
    for i in range(1, 10):
        fp = os.path.join(scripts_dir, f'generate_recipes_data_p{i}.json')
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            chunk = data if isinstance(data, list) else data.get('recipes', [])
            recipes.extend(chunk)
            print(f"[✓] Loaded {len(chunk)} from p{i}")

    if recipes:
        return recipes

    print("[✗] ERROR: No recipe files found!")
    print("    Expected one of:")
    for fp in candidates:
        print(f"    {fp}")
    return []


def prepare_dataset(recipes):
    """Build training samples from recipe list."""
    texts  = []
    labels = []
    names  = []

    for recipe in recipes:
        text  = build_recipe_text(recipe)
        label = guess_category(recipe)

        texts.append(text)
        labels.append(label)

        n = recipe.get('names', {})
        if isinstance(n, dict):
            nm = n.get('english', '') or n.get('en', '')
        else:
            nm = str(n) if n else ''
        names.append(nm or recipe.get('name', 'Unknown'))

    return texts, labels, names


if __name__ == '__main__':
    print("=" * 60)
    print("STEP 1 — DATA PREPARATION CHECK")
    print("=" * 60)

    recipes = load_recipes()
    if not recipes:
        print("\n[!] Fix file path issue above before continuing.")
        exit(1)

    texts, labels, names = prepare_dataset(recipes)

    print(f"\n[✓] Total recipes loaded: {len(texts)}")

    # Category distribution
    from collections import Counter
    dist = Counter(labels)
    print("\n[Category Distribution]")
    for cat_id, count in sorted(dist.items()):
        bar = '█' * count
        print(f"  {CATEGORY_NAMES[cat_id]:12s} ({cat_id}): {count:3d}  {bar}")

    # Sample outputs
    print("\n[Sample Recipe Texts]")
    for i in [0, 1, 2]:
        if i < len(texts):
            print(f"\n  Recipe: {names[i]}")
            print(f"  Label:  {CATEGORY_NAMES[labels[i]]} ({labels[i]})")
            print(f"  Text:   {texts[i][:120]}...")

    # Save prepared data for use in training
    import json
    output = []
    for t, l, n in zip(texts, labels, names):
        output.append({'text': t, 'label': l, 'name': n})

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sbert_training_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Training data saved to: sbert_training_data.json")
    print(f"[✓] Ready for Step 2 — run: python step2_train_sbert.py")
