from dotenv import load_dotenv
import os as _os
import sys as _sys

# ── Ensure cooking_assistant/ is always on path (works from Backend/ or cooking_assistant/) ──
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

# ── Load .env from cooking_assistant/.env ────────────────────────────────────
load_dotenv(dotenv_path=_os.path.join(_os.path.dirname(__file__), '.env'))

from flask import Blueprint, request, jsonify
import re
import json
import base64
from werkzeug.utils import secure_filename
from groq import Groq

cooking_bp = Blueprint('cooking', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ── Groq client ───────────────────────────────────────────────────────────────
GROQ_API_KEY = _os.environ.get("GROQ_API_KEY") or "dummy_key"
groq_client  = Groq(api_key=GROQ_API_KEY)

# ── Ingredient categories ─────────────────────────────────────────────────────
INGREDIENT_CATEGORIES = {
    '🥬 Vegetables & Herbs': [
        'onion','tomato','garlic','ginger','chili','curry leaves','pandan','leeks','spinach',
        'eggplant','brinjal','potato','carrot','beans','pumpkin','jackfruit','beetroot',
        'mushroom','gourd','drumstick','green chili','capsicum','lemon','lime','mango',
        'plantain','breadfruit','cucumber','coriander','mint','spring onion','shallot'
    ],
    '🍗 Protein': [
        'chicken','fish','prawn','crab','squid','egg','mutton','lamb','beef','pork','tuna',
        'sardine','shrimp','liver','duck','venison','lentil','chickpea','cashew','soya',
        'dal','parippu','anchovy','maldive'
    ],
    '🌾 Grains & Carbs': [
        'rice','flour','semolina','bread','roti','noodle','pasta','wheat','oat',
        'string hopper','hopper','pittu','idiyappam'
    ],
    '🌶️ Spices & Condiments': [
        'curry powder','turmeric','cumin','coriander powder','cardamom','cinnamon',
        'clove','fenugreek','mustard','black pepper','chili powder','goraka',
        'tamarind','vinegar','soy sauce','sugar','salt','maldive fish',
        'roasted curry','lemongrass','bay leaf'
    ],
    '🥛 Dairy & Coconut': [
        'coconut milk','coconut cream','coconut','yogurt','milk','butter',
        'ghee','cream','desiccated coconut'
    ],
    '🫙 Pantry': [
        'oil','water','stock','sauce','paste','baking powder',
        'baking soda','cornflour','food colour'
    ],
}

MEAL_PARSE_PROMPT = """
You are a meal plan parser. Extract the meal plan from the user's text.
Return ONLY a JSON object like this (no extra text):
{
  "monday":    {"breakfast": "", "lunch": "", "dinner": ""},
  "tuesday":   {"breakfast": "", "lunch": "", "dinner": ""},
  "wednesday": {"breakfast": "", "lunch": "", "dinner": ""},
  "thursday":  {"breakfast": "", "lunch": "", "dinner": ""},
  "friday":    {"breakfast": "", "lunch": "", "dinner": ""},
  "saturday":  {"breakfast": "", "lunch": "", "dinner": ""},
  "sunday":    {"breakfast": "", "lunch": "", "dinner": ""}
}
Leave fields empty string "" if not mentioned.
"""

MAIN_PROTEINS = [
    'chicken', 'fish', 'prawn', 'crab', 'mutton', 'lamb', 'beef', 'pork',
    'egg', 'tuna', 'sardine', 'shrimp', 'lentil', 'dhal', 'parippu',
]


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _load_recipes():
    data_dir = _os.path.join(_os.path.dirname(__file__), 'rag', 'data')
    for fname in ['recipes_all_merged.json', 'new_200_recipes.json', 'recipe_database.json']:
        fp = _os.path.join(data_dir, fname)
        if _os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('recipes', []) if isinstance(data, dict) else data

    recipes = []
    scripts_dir = _os.path.join(_os.path.dirname(__file__), '..', 'scripts')
    for i in range(1, 10):
        fp = _os.path.join(scripts_dir, f'generate_recipes_data_p{i}.json')
        if _os.path.exists(fp):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    recipes.extend(data)
            except Exception as e:
                print(f"[routes] Error loading p{i}: {e}")

    if recipes:
        return recipes

    print("[routes] WARNING: No recipe database found!")
    return []


def _get_recipe_name(recipe):
    names = recipe.get('names', {})
    if isinstance(names, dict):
        en = names.get('english', '') or names.get('en', '')
    else:
        en = str(names) if names else ''
    return en or recipe.get('name', 'Unknown Recipe')


def _categorise(name):
    low = name.lower()
    for cat, keywords in INGREDIENT_CATEGORIES.items():
        if any(k in low for k in keywords):
            return cat
    return '🫙 Pantry'


def _scale_amount(amount_str, num_people, recipe_servings):
    NON_SCALABLE = {'to taste', 'as needed', 'as required', 'a pinch', 'few', 'some', ''}
    if not amount_str or amount_str.lower().strip() in NON_SCALABLE:
        return {'value': 0, 'unit': amount_str or ''}

    scale = num_people / max(1, recipe_servings)
    match = re.match(r'^([\d]+(?:[./][\d]+)?(?:\.\d+)?)\s*(.*)', amount_str.strip())
    if not match:
        return {'value': 0, 'unit': amount_str}

    num_str = match.group(1)
    unit    = match.group(2).strip()

    try:
        if '/' in num_str:
            parts = num_str.split('/')
            num   = float(parts[0]) / float(parts[1])
        else:
            num = float(num_str)
        scaled = round(num * scale, 2)
        return {'value': int(scaled) if scaled == int(scaled) else scaled, 'unit': unit}
    except (ValueError, ZeroDivisionError):
        return {'value': 0, 'unit': amount_str}


def _build_recipe_lookup(recipes):
    lookup = {}
    for r in recipes:
        name = _get_recipe_name(r).lower().strip()
        if name:
            lookup[name] = r
    return lookup


def _ingredient_matches(user_word, recipe_ing_name):
    u = user_word.lower().strip()
    r = recipe_ing_name.lower().strip()
    if not u or not r:
        return False
    if u in r or r in u:
        return True
    for word in u.split():
        if len(word) >= 3 and word in r:
            return True
    for word in r.split():
        if len(word) >= 3 and word in u:
            return True
    return False


def _keyword_search(user_ingredients, recipes, top_k=12):
    """Fallback keyword-based recipe search used when SBERT is unavailable."""
    results = []
    for recipe in recipes:
        en_name    = _get_recipe_name(recipe)
        name_lower = en_name.lower()

        recipe_ings = []
        has_placeholder = False
        for ing in recipe.get('ingredients', []):
            name = ing.get('name', '') if isinstance(ing, dict) else str(ing)
            if isinstance(name, dict):
                name = name.get('english', '')
            
            if "ingredients to be added" in name.lower():
                has_placeholder = True
                break

            clean = re.sub(r'^[\d./\s]+(g|kg|ml|l|cup|tsp|tbsp|oz|lb)?\s*', '', name.lower().strip())
            if clean:
                recipe_ings.append(clean)

        method = recipe.get('method', '') or recipe.get('instructions', '')
        if not method or "instructions to be added" in method.lower() or "detailed cooking instructions" in method.lower():
            has_placeholder = True

        if has_placeholder or not recipe_ings:
            continue

        covered_ings = []
        missing_ings = []
        for ri in recipe_ings:
            if any(_ingredient_matches(ui, ri) for ui in user_ingredients):
                covered_ings.append(ri)
            else:
                missing_ings.append(ri)

        covered_count = len(covered_ings)
        total_count   = len(recipe_ings)
        base_score    = round((covered_count / total_count) * 100) if total_count else 0

        main_ing_match = any(
            p in name_lower and any(_ingredient_matches(p, ui) for ui in user_ingredients)
            for p in MAIN_PROTEINS
        )
        if main_ing_match:
            base_score = min(100, base_score + 20)

        if covered_count == 0 or base_score < 10:
            continue

        matched_display = [
            ui for ui in user_ingredients
            if any(_ingredient_matches(ui, ri) for ri in covered_ings)
        ]

        cook_mins = recipe.get('cook_time_mins', recipe.get('cook_time_minutes', 30))
        prep_mins = recipe.get('prep_time_mins', recipe.get('prep_time_minutes', 10))
        method    = recipe.get('method', '') or recipe.get('instructions', '')

        results.append({
            'id':                  recipe.get('id', ''),
            'name':                en_name,
            'match_score':         base_score,
            'matched_ingredients': matched_display,
            'missing_ingredients': missing_ings[:8],
            'ingredients_used':    matched_display,
            'ingredients':         recipe.get('ingredients', []),
            'cuisine':             'Sri Lankan',
            'category':            recipe.get('category', ''),
            'region':              recipe.get('region', ''),
            'difficulty':          recipe.get('difficulty', 'medium'),
            'cooking_time':        f"{cook_mins + prep_mins} mins",
            'cook_time_mins':      cook_mins,
            'prep_time_mins':      prep_mins,
            'servings':            recipe.get('servings', 4),
            'spice_level':         recipe.get('spice_level', 2),
            'is_authentic':        recipe.get('is_authentic', True),
            'instructions':        recipe.get('instructions', method),
            'method':              method,
            'tips':                recipe.get('tips', ''),
            'cultural_note':       recipe.get('cultural_note', ''),
            'description':         recipe.get('description', ''),
            'search_method':       'keyword-fallback',
        })

    results.sort(key=lambda x: (
        any(p in x['name'].lower() and any(_ingredient_matches(p, ui)
            for ui in user_ingredients) for p in MAIN_PROTEINS),
        x['match_score']
    ), reverse=True)

    return results[:top_k]


# ═════════════════════════════════════════════════════════════════════════════
# ROUTES — COOKING ASSISTANT
# ═════════════════════════════════════════════════════════════════════════════

@cooking_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        filename   = secure_filename(file.filename)
        upload_dir = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), 'uploads')
        _os.makedirs(upload_dir, exist_ok=True)
        filepath   = _os.path.join(upload_dir, filename)
        file.save(filepath)

        from image_processor import analyze_image
        result = analyze_image(filepath)

        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', 'Failed to detect ingredients')})

        detected = result.get('ingredients', [])
        return jsonify({
            'success':        True,
            'ingredients':    detected,
            'total_detected': len(detected),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cooking_bp.route('/search-recipes', methods=['POST'])
def search_recipes():
    data = request.get_json()
    if not data or 'ingredients' not in data:
        return jsonify({'error': 'No ingredients provided'}), 400

    user_ingredients = [i.lower().strip() for i in data['ingredients']]
    recipes          = _load_recipes()
    method_used      = 'keyword-fallback'
    results          = []

    # ── SBERT semantic search (with automatic keyword fallback) ───────────────
    try:
        from sbert_matcher import sbert_search_recipes
        results     = sbert_search_recipes(user_ingredients, recipes, top_k=12)
        method_used = 'sentence-bert'
        print(f"[SBERT] ✓ {len(results)} recipes found semantically")
    except Exception as e:
        print(f"[SBERT] ✗ Falling back to keyword: {e}")
        results = _keyword_search(user_ingredients, recipes)

    return jsonify({
        'success':       True,
        'recipes':       results,
        'total_found':   len(results),
        'database_size': len(recipes),
        'search_method': method_used,
    })


@cooking_bp.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    for r in _load_recipes():
        if r.get('id') == recipe_id:
            return jsonify({'success': True, 'recipe': r}), 200
    return jsonify({'error': 'Recipe not found'}), 404


@cooking_bp.route('/test-api', methods=['GET'])
def test_api():
    try:
        from image_processor import test_api_connection
        success, message = test_api_connection()
    except Exception as e:
        success, message = False, str(e)
    return jsonify({'api_working': success, 'message': message}), 200 if success else 500


@cooking_bp.route('/sbert-status', methods=['GET'])
def sbert_status():
    """Open in browser to confirm SBERT model is loaded and working."""
    try:
        from sbert_matcher import sbert_predict_category
        cat, conf = sbert_predict_category(
            "Chicken Curry. Ingredients: chicken, onion, coconut milk, curry powder"
        )
        return jsonify({
            'sbert_loaded': True,
            'test_input':   'Chicken Curry with chicken, onion, coconut milk',
            'predicted':    cat,
            'confidence':   conf,
            'status':       '✅ SBERT is working correctly'
        })
    except Exception as e:
        return jsonify({
            'sbert_loaded': False,
            'error':        str(e),
            'status':       '❌ SBERT not available — using keyword fallback'
        })


# ═════════════════════════════════════════════════════════════════════════════
# ROUTES — MEAL PLANNER
# ═════════════════════════════════════════════════════════════════════════════

@cooking_bp.route('/parse-meal-plan', methods=['POST'])
def parse_meal_plan():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    try:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": MEAL_PARSE_PROMPT},
                {"role": "user",   "content": data['text']},
            ],
            temperature=0.1,
            max_tokens=800,
        )
        raw   = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return jsonify({'success': False, 'error': 'Could not parse meal plan'}), 200
        return jsonify({'success': True, 'meal_plan': json.loads(match.group())}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cooking_bp.route('/parse-meal-plan-image', methods=['POST'])
def parse_meal_plan_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    try:
        b64  = base64.b64encode(file.read()).decode('utf-8')
        ext  = file.filename.rsplit('.', 1)[-1].lower()
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'png': 'image/png',  'gif':  'image/gif'}.get(ext, 'image/jpeg')

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text",      "text": f"Read this meal plan image carefully.\n\n{MEAL_PARSE_PROMPT}"},
                ],
            }],
            max_tokens=800,
        )
        raw   = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return jsonify({'success': False, 'error': 'Could not read meal plan from image'}), 200
        return jsonify({'success': True, 'meal_plan': json.loads(match.group())}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cooking_bp.route('/grocery-from-meals', methods=['POST'])
def grocery_from_meals():
    data = request.get_json()
    if not data or 'meals' not in data:
        return jsonify({'error': 'No meals provided'}), 400

    meal_names = [m.lower().strip() for m in data['meals'] if m]
    num_people = max(1, int(data.get('num_people', 1)))
    recipes    = _load_recipes()
    lookup     = _build_recipe_lookup(recipes)

    print(f"[grocery] {num_people} people · {len(meal_names)} meals")

    agg             = {}
    matched_recipes = []
    unmatched       = []

    for meal in meal_names:
        recipe = lookup.get(meal)
        if not recipe:
            for key, val in lookup.items():
                if meal in key or key in meal:
                    recipe = val
                    break

        if not recipe:
            unmatched.append(meal)
            continue

        recipe_name     = _get_recipe_name(recipe)
        recipe_servings = max(1, int(recipe.get('servings', 4)))
        matched_recipes.append(recipe_name)

        for ing in recipe.get('ingredients', []):
            raw_name   = ing.get('name', '')   if isinstance(ing, dict) else str(ing)
            raw_amount = ing.get('amount', '') if isinstance(ing, dict) else ''
            if isinstance(raw_name, dict):
                raw_name = raw_name.get('english', '')

            name = raw_name.strip().lower()
            if not name:
                continue

            scaled = _scale_amount(raw_amount, num_people, recipe_servings)

            if name in agg:
                existing = agg[name]
                if scaled['unit'] and scaled['unit'] == existing['unit'] and scaled['value']:
                    existing['total'] = round(existing['total'] + scaled['value'], 2)
                else:
                    existing['count'] += 1
            else:
                agg[name] = {
                    'total': scaled['value'],
                    'unit':  scaled['unit'],
                    'raw':   raw_amount,
                    'count': 1,
                }

    categories = {cat: [] for cat in INGREDIENT_CATEGORIES}

    for name, info in agg.items():
        cat = _categorise(name)
        if cat not in categories:
            categories[cat] = []

        if info['unit'] and info['total']:
            display = f"{info['total']} {info['unit']}"
        elif info['raw'] in ('to taste', 'as needed', 'as required'):
            display = info['raw']
        elif info['total']:
            display = str(info['total'])
        elif info['raw']:
            display = info['raw']
        else:
            display = f"×{info['count']}"

        if info['count'] > 1 and info['unit']:
            display += f" (×{info['count']} recipes)"

        categories[cat].append({
            'name':          name.title(),
            'scaled_amount': display,
            'for_people':    num_people,
        })

    categories = {
        cat: sorted(items, key=lambda x: x['name'])
        for cat, items in categories.items() if items
    }

    total_items = sum(len(v) for v in categories.values())
    print(f"[grocery] {total_items} items · {len(matched_recipes)} matched · {len(unmatched)} unmatched")

    return jsonify({
        'success': True,
        'grocery': {
            'categories':    categories,
            'total_items':   total_items,
            'total_meals':   len(matched_recipes),
            'matched_meals': matched_recipes,
            'num_people':    num_people,
        },
        'unmatched_meals': unmatched,
    }), 200