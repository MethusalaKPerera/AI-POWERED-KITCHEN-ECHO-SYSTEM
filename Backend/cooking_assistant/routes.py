from dotenv import load_dotenv
load_dotenv()

from flask import Blueprint, request, jsonify
import os
import re
import json
import base64
from werkzeug.utils import secure_filename
from groq import Groq

cooking_bp = Blueprint('cooking', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ── Groq client ───────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client  = Groq(api_key=GROQ_API_KEY)

# ── Ingredient categories ─────────────────────────────────────────────────────
INGREDIENT_CATEGORIES = {
    '🥬 Vegetables & Herbs':  ['onion','tomato','garlic','ginger','chili','curry leaves','pandan','leeks','spinach','eggplant','brinjal','potato','carrot','beans','pumpkin','jackfruit','beetroot','mushroom','gourd','drumstick','green chili','capsicum','lemon','lime','mango','plantain','breadfruit','cucumber','coriander','mint','spring onion','shallot'],
    '🍗 Protein':              ['chicken','fish','prawn','crab','squid','egg','mutton','lamb','beef','pork','tuna','sardine','shrimp','liver','duck','venison','lentil','chickpea','cashew','soya','dal','parippu','anchovy','maldive'],
    '🌾 Grains & Carbs':       ['rice','flour','semolina','bread','roti','noodle','pasta','wheat','oat','string hopper','hopper','pittu','idiyappam'],
    '🌶️ Spices & Condiments': ['curry powder','turmeric','cumin','coriander powder','cardamom','cinnamon','clove','fenugreek','mustard','black pepper','chili powder','goraka','tamarind','vinegar','soy sauce','sugar','salt','maldive fish','roasted curry','lemongrass','bay leaf'],
    '🥛 Dairy & Coconut':      ['coconut milk','coconut cream','coconut','yogurt','milk','butter','ghee','cream','desiccated coconut'],
    '🫙 Pantry':               ['oil','water','stock','sauce','paste','baking powder','baking soda','cornflour','food colour'],
}

MEAL_PARSE_PROMPT = """
You are a meal plan parser. Extract the meal plan from the user's text.
Return ONLY a JSON object like this (no extra text):
{
  "monday":    {"breakfast": "", "lunch": "Rice & Curry", "dinner": "Kottu Roti"},
  "tuesday":   {"breakfast": "Hoppers", "lunch": "", "dinner": ""},
  "wednesday": {"breakfast": "", "lunch": "", "dinner": ""},
  "thursday":  {"breakfast": "", "lunch": "", "dinner": ""},
  "friday":    {"breakfast": "", "lunch": "", "dinner": ""},
  "saturday":  {"breakfast": "", "lunch": "", "dinner": ""},
  "sunday":    {"breakfast": "", "lunch": "", "dinner": ""}
}
Leave fields empty string "" if not mentioned.
Fill in the days/meals mentioned by the user. Be flexible with day names and meal names.
"""


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _load_recipes():
    """Load recipes from merged database files."""
    data_dir = os.path.join(os.path.dirname(__file__), 'rag', 'data')
    for fname in ['recipes_all_merged.json', 'new_200_recipes.json', 'recipe_database.json']:
        fp = os.path.join(data_dir, fname)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('recipes', []) if isinstance(data, dict) else data

    # Fallback: load generate_recipes_data_p1..p9.json from scripts folder
    recipes = []
    scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
    for i in range(1, 10):
        fp = os.path.join(scripts_dir, f'generate_recipes_data_p{i}.json')
        if os.path.exists(fp):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    recipes.extend(data)
                    print(f"[routes] Loaded {len(data)} recipes from p{i}")
            except Exception as e:
                print(f"[routes] Error loading p{i}: {e}")

    if recipes:
        return recipes

    print("[routes] WARNING: No recipe database found!")
    return []


def _categorise(ingredient_name):
    """Return the display category for an ingredient name."""
    low = ingredient_name.lower()
    for cat, keywords in INGREDIENT_CATEGORIES.items():
        if any(k in low for k in keywords):
            return cat
    return '🫙 Pantry'


def _scale_amount(amount_str, num_people, recipe_servings):
    """
    Parse an amount string and scale it by (num_people / recipe_servings).
    Returns {'value': float|int, 'unit': str}

    Examples:
        '2 cups',  4 people, 4 servings -> value=2,   unit='cups'
        '2 cups',  2 people, 4 servings -> value=1,   unit='cups'
        '2 cups',  6 people, 4 servings -> value=3,   unit='cups'
        '1/2 cup', 4 people, 4 servings -> value=0.5, unit='cup'
        'to taste'                       -> value=0,   unit='to taste'
    """
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
            num = float(parts[0]) / float(parts[1])
        else:
            num = float(num_str)

        scaled = round(num * scale, 2)
        return {'value': int(scaled) if scaled == int(scaled) else scaled, 'unit': unit}
    except (ValueError, ZeroDivisionError):
        return {'value': 0, 'unit': amount_str}


def _build_recipe_lookup(recipes):
    """Build a name->recipe dict for fast fuzzy lookup."""
    lookup = {}
    for r in recipes:
        names = r.get('names', {})
        en = (names.get('english', '') if isinstance(names, dict) else str(names)).lower().strip()
        if en:
            lookup[en] = r
        alt = r.get('name', '').lower().strip()
        if alt:
            lookup[alt] = r
    return lookup


# ═════════════════════════════════════════════════════════════════════════════
# ROUTES — COOKING ASSISTANT
# ═════════════════════════════════════════════════════════════════════════════

@cooking_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Upload and analyze ingredient image using Groq Vision API."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed'}), 400

    try:
        filename   = secure_filename(file.filename)
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath   = os.path.join(upload_dir, filename)
        file.save(filepath)

        from image_processor import detect_ingredients
        detected = detect_ingredients(filepath)

        return jsonify({
            'success':        True,
            'ingredients':    detected,
            'message':        f'Detected {len(detected)} ingredients using Groq Vision AI',
            'image_path':     filepath,
            'total_detected': len(detected),
        }), 200

    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500


@cooking_bp.route('/search-recipes', methods=['POST'])
def search_recipes():
    """Search recipes by ingredients using real recipe database."""
    data = request.get_json()
    if not data or 'ingredients' not in data:
        return jsonify({'error': 'No ingredients provided'}), 400

    user_ingredients = [i.lower().strip() for i in data['ingredients']]
    recipes          = _load_recipes()

    if not recipes:
        return jsonify({'success': False, 'error': 'Recipe database not found.', 'recipes': []}), 200

    scored = []
    for recipe in recipes:
        recipe_ings = []
        for ing in recipe.get('ingredients', []):
            name = ing.get('name', '') if isinstance(ing, dict) else str(ing)
            if isinstance(name, dict):
                name = name.get('english', '')
            recipe_ings.append(name.lower().strip())

        if not recipe_ings:
            continue

        matched = []
        for ui in user_ingredients:
            for ri in recipe_ings:
                if ri and (ui in ri or ri.split()[0] in ui):
                    matched.append(ui)
                    break

        missing = [ri for ri in recipe_ings if ri and not any(
            ui in ri or ri.split()[0] in ui for ui in user_ingredients
        )]

        match_pct = round((len(matched) / len(recipe_ings)) * 100) if recipe_ings else 0
        if match_pct == 0:
            continue

        names   = recipe.get('names', {})
        en_name = (names.get('english', '') or names.get('en', '') if isinstance(names, dict) else str(names)) \
                  or recipe.get('name', 'Unknown Recipe')

        cook_mins = recipe.get('cook_time_mins',  recipe.get('cook_time_minutes',  30))
        prep_mins = recipe.get('prep_time_mins',  recipe.get('prep_time_minutes',  10))
        method    = recipe.get('method', '') or recipe.get('instructions', '')

        scored.append({
            'id':                  recipe.get('id', ''),
            'name':                en_name,
            'match_score':         match_pct,
            'matched_ingredients': matched,
            'missing_ingredients': missing[:8],
            'ingredients_used':    matched,
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
            'source':              'RAG Database',
        })

    scored.sort(key=lambda x: x['match_score'], reverse=True)

    return jsonify({
        'success':       True,
        'recipes':       scored[:12],
        'total_found':   len(scored),
        'search_query':  user_ingredients,
        'database_size': len(recipes),
    }), 200


@cooking_bp.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get full recipe details by ID."""
    for r in _load_recipes():
        if r.get('id') == recipe_id:
            return jsonify({'success': True, 'recipe': r}), 200
    return jsonify({'error': 'Recipe not found'}), 404


@cooking_bp.route('/test-api', methods=['GET'])
def test_api():
    """Test if Groq Vision API is working."""
    try:
        from image_processor import test_api_connection
        success, message = test_api_connection()
    except Exception as e:
        success, message = False, str(e)
    return jsonify({'api_working': success, 'message': message}), 200 if success else 500


# ═════════════════════════════════════════════════════════════════════════════
# ROUTES — MEAL PLANNER
# ═════════════════════════════════════════════════════════════════════════════

@cooking_bp.route('/parse-meal-plan', methods=['POST'])
def parse_meal_plan():
    """Parse free-text meal plan using Groq AI."""
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
            max_tokens=800,
            temperature=0.1,
        )
        raw   = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return jsonify({'success': False, 'error': 'Could not parse meal plan from text'}), 200

        return jsonify({'success': True, 'meal_plan': json.loads(match.group())}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cooking_bp.route('/parse-meal-plan-image', methods=['POST'])
def parse_meal_plan_image():
    """Parse meal plan from an uploaded image using Groq Vision."""
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
            temperature=0.1,
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
    """
    Build a categorised, properly-scaled grocery list from meal names.
    Scales every ingredient amount by (num_people / recipe_servings).
    """
    data = request.get_json()
    if not data or 'meals' not in data:
        return jsonify({'error': 'No meals provided'}), 400

    meal_names = [m.lower().strip() for m in data['meals'] if m]
    num_people = max(1, int(data.get('num_people', 1)))
    recipes    = _load_recipes()
    lookup     = _build_recipe_lookup(recipes)

    print(f"[grocery] {num_people} people · {len(meal_names)} meals")

    # ── Aggregate scaled ingredients ──────────────────────────────────────────
    agg             = {}   # name → {total, unit, raw, count}
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

        recipe_name     = (recipe.get('names', {}) or {}).get('english', '') or recipe.get('name', meal)
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

    # ── Build categorised output ──────────────────────────────────────────────
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

    # Sort & remove empty categories
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