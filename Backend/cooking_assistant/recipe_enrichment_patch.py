"""
PATCH for routes.py — add this helper function and update the search-recipes endpoint
to return full recipe data including method/instructions/ingredients from your JSON files.

INSTRUCTIONS:
1. Open Backend/cooking_assistant/routes.py
2. Find the /api/search-recipes route
3. Add the load_full_recipe() helper below
4. In the search-recipes route, call enrich_recipes() before returning

------- ADD THIS NEAR THE TOP OF routes.py (after imports) -------
"""

import json
import os
import glob

# Path to your recipe JSON files — adjust if different
RECIPE_DATA_DIRS = [
    os.path.join(os.path.dirname(__file__), '..', '..', 'rag', 'data', 'recipes'),
    os.path.join(os.path.dirname(__file__), 'data', 'recipes'),
    os.path.join(os.path.dirname(__file__), '..', 'data'),
]

# Cache loaded recipes in memory
_RECIPE_CACHE = {}

def _load_all_recipes():
    """Load all recipe JSON files into memory cache."""
    global _RECIPE_CACHE
    if _RECIPE_CACHE:
        return _RECIPE_CACHE

    loaded = {}

    for data_dir in RECIPE_DATA_DIRS:
        if not os.path.isdir(data_dir):
            continue

        # Load individual recipe files (recipe_078.json, SL_0191.json, etc.)
        for filepath in glob.glob(os.path.join(data_dir, '*.json')):
            fname = os.path.basename(filepath)
            # Skip database files
            if 'database' in fname or 'combined' in fname or 'generate' in fname:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # It might be a list or a dict with 'recipes' key
                    if isinstance(data, list):
                        for r in data:
                            if isinstance(r, dict):
                                rid = r.get('id', '') or r.get('name', '')
                                name = (r.get('names', {}) or {}).get('english', '') or r.get('name', '')
                                if name:
                                    loaded[name.lower()] = r
                                    if rid:
                                        loaded[str(rid).lower()] = r
                    elif isinstance(data, dict) and 'recipes' in data:
                        for r in data['recipes']:
                            if isinstance(r, dict):
                                name = (r.get('names', {}) or {}).get('english', '') or r.get('name', '')
                                rid = r.get('id', '')
                                if name:
                                    loaded[name.lower()] = r
                                    if rid:
                                        loaded[str(rid).lower()] = r
                except Exception:
                    pass
            else:
                # Individual recipe file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        r = json.load(f)
                    if isinstance(r, dict):
                        name = (r.get('names', {}) or {}).get('english', '') or r.get('name', '')
                        rid = r.get('id', '')
                        if name:
                            loaded[name.lower()] = r
                        if rid:
                            loaded[str(rid).lower()] = r
                except Exception:
                    pass

    # Also check the generate_recipes_data JSON files in the same dir as routes.py
    script_dir = os.path.dirname(__file__)
    for filepath in glob.glob(os.path.join(script_dir, 'generate_recipes_data_*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                for r in data:
                    if isinstance(r, dict):
                        name = (r.get('names', {}) or {}).get('english', '') or r.get('name', '')
                        rid = r.get('id', '')
                        if name:
                            loaded[name.lower()] = r
                        if rid:
                            loaded[str(rid).lower()] = r
        except Exception:
            pass

    _RECIPE_CACHE = loaded
    print(f"[routes] Loaded {len(loaded)} recipes into cache")
    return loaded


def enrich_recipe(recipe_result: dict) -> dict:
    """
    Merge a ChromaDB/search result with the full recipe data from JSON files.
    Adds method, tips, cultural_note, full ingredients list, spice_level, etc.
    """
    all_recipes = _load_all_recipes()

    name = (recipe_result.get('name', '') or '').lower()
    rid  = (recipe_result.get('id', '')   or '').lower()

    full = all_recipes.get(name) or all_recipes.get(rid)

    if not full:
        # Fuzzy match: check if any key contains the recipe name
        for key, val in all_recipes.items():
            if name and (name in key or key in name):
                full = val
                break

    if not full:
        return recipe_result  # Return as-is if not found

    # Merge: full data wins for missing fields
    enriched = dict(recipe_result)

    # Add instructions/method
    if not enriched.get('instructions') and not enriched.get('method'):
        enriched['method'] = full.get('method', '')
        enriched['instructions'] = full.get('method', '')

    # Add tips
    if not enriched.get('tips'):
        enriched['tips'] = full.get('tips', '')

    # Add cultural note
    if not enriched.get('cultural_note'):
        enriched['cultural_note'] = full.get('cultural_note', '')

    # Add full ingredients list with amounts
    if not enriched.get('ingredients') or len(enriched.get('ingredients', [])) == 0:
        enriched['ingredients'] = full.get('ingredients', [])

    # Add extra metadata
    if not enriched.get('region'):
        enriched['region'] = full.get('region', '')
    if not enriched.get('spice_level'):
        enriched['spice_level'] = full.get('spice_level', 0)
    if not enriched.get('difficulty') or enriched['difficulty'] == 'unknown':
        enriched['difficulty'] = full.get('difficulty', '')
    if not enriched.get('cooking_time'):
        mins = full.get('cook_time_mins', 0) + full.get('prep_time_mins', 0)
        if mins:
            enriched['cooking_time'] = f"{mins} mins"
            enriched['cook_time_mins'] = full.get('cook_time_mins', 0)

    return enriched


def enrich_recipes(recipe_list: list) -> list:
    """Enrich a list of recipe results with full data."""
    return [enrich_recipe(r) for r in recipe_list]


"""
------- NOW UPDATE YOUR search-recipes ROUTE in routes.py -------

Find something like this:

@bp.route('/api/search-recipes', methods=['POST'])
def search_recipes():
    ...
    recipes = search_result  # or however you get your results
    return jsonify({'success': True, 'recipes': recipes})

CHANGE THE RETURN LINE TO:

    from routes import enrich_recipes   # if in same file, just call directly
    return jsonify({'success': True, 'recipes': enrich_recipes(recipes)})

------- OR if routes.py already has a search function, just add these 2 lines -------

After you get your recipe results, add:
    # Enrich with full recipe data
    recipes = enrich_recipes(recipes)

Then return as normal.
"""