## ══════════════════════════════════════════════════════════════════════
## STEP 4 — UPDATE routes.py
## ══════════════════════════════════════════════════════════════════════
##
## Find the @cooking_bp.route('/search-recipes') function in your
## routes.py and REPLACE THE ENTIRE FUNCTION with this:
##
## ══════════════════════════════════════════════════════════════════════


@cooking_bp.route('/search-recipes', methods=['POST'])
def search_recipes():
    data = request.get_json()
    if not data or 'ingredients' not in data:
        return jsonify({'error': 'No ingredients provided'}), 400

    user_ingredients = [i.lower().strip() for i in data['ingredients']]
    recipes          = _load_recipes()

    # ── Sentence-BERT semantic search ──────────────────────────────────
    # This replaces the old keyword matching with semantic understanding.
    # Sentence-BERT converts both user ingredients and recipes into
    # 384-dimensional meaning vectors, then finds recipes whose meaning
    # is closest to what the user has available.
    try:
        from sbert_matcher import sbert_search_recipes
        results = sbert_search_recipes(user_ingredients, recipes, top_k=12)
        method_used = 'sentence-bert'

    except Exception as e:
        # Graceful fallback to keyword matching if SBERT fails
        print(f"[SBERT] Fallback to keyword matching: {e}")
        results     = _keyword_search(user_ingredients, recipes)
        method_used = 'keyword-fallback'

    return jsonify({
        'success':       True,
        'recipes':       results,
        'total_found':   len(results),
        'database_size': len(recipes),
        'search_method': method_used,   # useful to verify SBERT is being used
    })


## ══════════════════════════════════════════════════════════════════════
## Also add this fallback function somewhere above search_recipes
## (it's used if SBERT fails for any reason)
## ══════════════════════════════════════════════════════════════════════

def _keyword_search(user_ingredients, recipes, top_k=12):
    """Original keyword-based fallback search."""
    results = []
    for recipe in recipes:
        en_name    = _get_recipe_name(recipe)
        recipe_ings = []
        for ing in recipe.get('ingredients', []):
            name = ing.get('name', '') if isinstance(ing, dict) else str(ing)
            if isinstance(name, dict):
                name = name.get('english', '')
            clean = re.sub(
                r'^\d+[\d./]*\s*(g|kg|ml|l|cup|tsp|tbsp|oz|lb|piece|pieces)?\s*',
                '', name.lower().strip(), flags=re.IGNORECASE
            )
            if clean:
                recipe_ings.append(clean)

        if not recipe_ings:
            continue

        covered = [ri for ri in recipe_ings
                   if any(_ingredient_matches(ui, ri)
                          for ui in user_ingredients)]
        missing = [ri for ri in recipe_ings if ri not in covered]

        score = round((len(covered) / len(recipe_ings)) * 100)
        if score < 10:
            continue

        protein_boost = any(
            p in en_name.lower() and any(
                _ingredient_matches(p, ui) for ui in user_ingredients
            )
            for p in MAIN_PROTEINS
        )
        if protein_boost:
            score = min(100, score + 20)

        cook_mins = recipe.get('cook_time_mins',
                     recipe.get('cook_time_minutes', 30))
        prep_mins = recipe.get('prep_time_mins',
                     recipe.get('prep_time_minutes', 10))
        method    = recipe.get('method', '') or recipe.get('instructions', '')

        results.append({
            'id':                    recipe.get('id', ''),
            'name':                  en_name,
            'match_score':           score,
            'matched_ingredients':   covered,
            'missing_ingredients':   missing[:8],
            'ingredients_used':      covered,
            'ingredients':           recipe.get('ingredients', []),
            'cuisine':               'Sri Lankan',
            'category':              recipe.get('category', ''),
            'region':                recipe.get('region', ''),
            'difficulty':            recipe.get('difficulty', 'medium'),
            'cooking_time':          f"{cook_mins + prep_mins} mins",
            'cook_time_mins':        cook_mins,
            'prep_time_mins':        prep_mins,
            'servings':              recipe.get('servings', 4),
            'spice_level':           recipe.get('spice_level', 2),
            'is_authentic':          recipe.get('is_authentic', True),
            'instructions':          recipe.get('instructions', method),
            'method':                method,
            'tips':                  recipe.get('tips', ''),
            'cultural_note':         recipe.get('cultural_note', ''),
            'description':           recipe.get('description', ''),
        })

    results.sort(key=lambda x: x['match_score'], reverse=True)
    return results[:top_k]
