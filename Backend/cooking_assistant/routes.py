from flask import Blueprint, request, jsonify
import os
import json
from werkzeug.utils import secure_filename

cooking_bp = Blueprint('cooking', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _load_recipes():
    """Load recipes from merged database"""
    data_dir = os.path.join(os.path.dirname(__file__), 'rag', 'data')
    for fname in ['recipes_all_merged.json', 'new_200_recipes.json', 'recipe_database.json']:
        fp = os.path.join(data_dir, fname)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data.get('recipes', [])
            return data

    # Also try loading the generate_recipes_data JSON files directly
    recipes = []
    script_dir = os.path.dirname(__file__)
    for i in range(1, 10):
        fp = os.path.join(script_dir, f'generate_recipes_data_p{i}.json')
        if os.path.exists(fp):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    recipes.extend(data)
                    print(f"[routes] Loaded {len(data)} recipes from generate_recipes_data_p{i}.json")
            except Exception as e:
                print(f"[routes] Error loading p{i}: {e}")

    if recipes:
        return recipes

    print("[routes] WARNING: No recipe database found!")
    return []


@cooking_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Upload and analyze ingredient image using Groq Vision API"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed'}), 400

    try:
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        from image_processor import detect_ingredients
        detected_ingredients = detect_ingredients(filepath)

        return jsonify({
            'success': True,
            'ingredients': detected_ingredients,
            'message': f'Detected {len(detected_ingredients)} ingredients using Groq Vision AI',
            'image_path': filepath,
            'total_detected': len(detected_ingredients)
        }), 200

    except Exception as e:
        print(f"Error in analyze_image: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500


@cooking_bp.route('/search-recipes', methods=['POST'])
def search_recipes():
    """Search recipes by ingredients using real recipe database"""
    data = request.get_json()

    if not data or 'ingredients' not in data:
        return jsonify({'error': 'No ingredients provided'}), 400

    user_ingredients = [i.lower().strip() for i in data['ingredients']]
    recipes = _load_recipes()

    if not recipes:
        return jsonify({
            'success': False,
            'error': 'Recipe database not found. Check your data files.',
            'recipes': []
        }), 200

    scored_recipes = []

    for recipe in recipes:
        # ── Get ingredient names from recipe ──────────────────────────────
        recipe_ings = []
        for ing in recipe.get('ingredients', []):
            name = ing.get('name', '') if isinstance(ing, dict) else str(ing)
            if isinstance(name, dict):
                name = name.get('english', '')
            recipe_ings.append(name.lower().strip())

        if not recipe_ings:
            continue

        # ── Calculate match score ─────────────────────────────────────────
        matched = []
        for ui in user_ingredients:
            for ri in recipe_ings:
                if ri and (ui in ri or ri.split()[0] in ui):
                    matched.append(ui)
                    break

        missing = [ri for ri in recipe_ings if not any(
            ui in ri or ri.split()[0] in ui for ui in user_ingredients
        ) and ri]

        match_pct = round((len(matched) / len(recipe_ings)) * 100) if recipe_ings else 0

        if match_pct == 0:
            continue

        # ── Get recipe name ───────────────────────────────────────────────
        names = recipe.get('names', {})
        if isinstance(names, dict):
            en_name = names.get('english', '') or names.get('en', '')
        else:
            en_name = str(names)

        # Fallback to 'name' field (used by batch_3 style recipes)
        if not en_name:
            en_name = recipe.get('name', 'Unknown Recipe')

        # ── Cook time ─────────────────────────────────────────────────────
        cook_mins  = recipe.get('cook_time_mins',  recipe.get('cook_time_minutes',  30))
        prep_mins  = recipe.get('prep_time_mins',  recipe.get('prep_time_minutes',  10))
        total_mins = cook_mins + prep_mins

        # ── Instructions: prefer 'method' field, then 'instructions' ─────
        method = recipe.get('method', '') or recipe.get('instructions', '')
        # If instructions is a list (batch_3 style), keep as list for frontend
        instructions_raw = recipe.get('instructions', method)

        # ── Build full recipe result ──────────────────────────────────────
        scored_recipes.append({
            # Identity
            'id':           recipe.get('id', ''),
            'name':         en_name,

            # Match info
            'match_score':           match_pct,
            'matched_ingredients':   matched,
            'missing_ingredients':   missing[:8],     # show up to 8
            'ingredients_used':      matched,

            # Full ingredients list WITH amounts
            'ingredients':  recipe.get('ingredients', []),

            # Cooking info
            'cuisine':        'Sri Lankan',
            'category':       recipe.get('category', ''),
            'region':         recipe.get('region', ''),
            'difficulty':     recipe.get('difficulty', 'medium'),
            'cooking_time':   f"{total_mins} mins",
            'cook_time_mins': cook_mins,
            'prep_time_mins': prep_mins,
            'servings':       recipe.get('servings', 4),
            'spice_level':    recipe.get('spice_level', 2),
            'is_authentic':   recipe.get('is_authentic', True),

            # Full recipe content  ← THIS IS WHAT WAS MISSING
            'instructions':   instructions_raw,
            'method':         method,
            'tips':           recipe.get('tips', ''),
            'cultural_note':  recipe.get('cultural_note', ''),
            'description':    recipe.get('description', ''),

            # Source
            'source': 'RAG Database',
        })

    # Sort by match score descending
    scored_recipes.sort(key=lambda x: x['match_score'], reverse=True)

    return jsonify({
        'success':      True,
        'recipes':      scored_recipes[:12],   # return top 12
        'total_found':  len(scored_recipes),
        'search_query': user_ingredients,
        'database_size': len(recipes)
    }), 200


@cooking_bp.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get full recipe details by ID"""
    recipes = _load_recipes()
    for r in recipes:
        if r.get('id') == recipe_id:
            return jsonify({'success': True, 'recipe': r}), 200
    return jsonify({'error': 'Recipe not found'}), 404


@cooking_bp.route('/generate-grocery-list', methods=['POST'])
def generate_grocery_list():
    """Generate grocery list from meal plan"""
    data = request.get_json()

    if not data or 'meal_plan' not in data:
        return jsonify({'error': 'No meal plan provided'}), 400

    meal_plan    = data['meal_plan']
    num_people   = data.get('num_people', 1)
    recipes      = _load_recipes()
    grocery      = {}
    recipe_lookup = {r.get('id', ''): r for r in recipes}

    for day_meals in meal_plan:
        if isinstance(day_meals, dict):
            for meal_type, recipe_id in day_meals.items():
                recipe = recipe_lookup.get(recipe_id)
                if recipe:
                    for ing in recipe.get('ingredients', []):
                        name   = ing.get('name', '')   if isinstance(ing, dict) else str(ing)
                        amount = ing.get('amount', '') if isinstance(ing, dict) else ''
                        if isinstance(name, dict):
                            name = name.get('english', '')
                        if name:
                            if name not in grocery:
                                grocery[name] = {'item': name, 'amount': amount, 'count': 0}
                            grocery[name]['count'] += num_people

    grocery_list = {
        'all_items': list(grocery.values()),
        'message': 'Add recipe IDs to your meal plan to generate a grocery list' if not grocery else ''
    }

    return jsonify({
        'success':     True,
        'grocery_list': grocery_list,
        'total_items':  len(grocery),
        'num_people':   num_people
    }), 200


@cooking_bp.route('/test-api', methods=['GET'])
def test_api():
    """Test if Groq Vision API is working"""
    try:
        from image_processor import test_api_connection
        success, message = test_api_connection()
    except Exception as e:
        success, message = False, str(e)

    return jsonify({
        'api_working': success,
        'message':     message
    }), 200 if success else 500

    """
ADD THESE 2 NEW ROUTES to your routes.py (Backend/cooking_assistant/routes.py)
Paste them at the END of the file, before the last closing line.

Also add this import at the very top of routes.py (with the other imports):
    import base64
    from groq import Groq

And add this near the top (after imports):
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_API_KEY)
"""

# ── paste these routes into routes.py ────────────────────────────────────────

import json
import base64
import os
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    # Provide a clear explanation if the key is missing rather than letting the
    # underlying library raise a generic error later when attempting to create
    # a client.  This helps users configure the environment correctly.
    raise RuntimeError(
        "GROQ_API_KEY environment variable is not set. "
        "Please export it or add it to your .env file before running the app."
    )
groq_client = Groq(api_key=GROQ_API_KEY)

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

INGREDIENT_CATEGORIES = {
    "🥬 Vegetables & Herbs":  ["onion","tomato","garlic","ginger","chili","curry leaves","pandan","leeks","spinach","eggplant","brinjal","potato","carrot","beans","pumpkin","jackfruit","beetroot","mushroom","gourd","drumstick","green","pepper","capsicum","lemon","lime","mango","plantain","breadfruit","cucumber","coriander","mint"],
    "🍗 Protein":              ["chicken","fish","prawn","crab","squid","egg","mutton","lamb","beef","pork","tuna","sardine","shrimp","liver","duck","venison","lentil","chickpea","cashew","soya","dal","parippu","anchovy","maldive"],
    "🌾 Grains & Carbs":       ["rice","flour","semolina","bread","roti","noodle","pasta","wheat","oat","hoppers","idiyappam","pittu","string hoppers"],
    "🌶️ Spices & Condiments": ["curry powder","turmeric","cumin","coriander powder","cardamom","cinnamon","clove","fenugreek","mustard","pepper","chili powder","goraka","tamarind","vinegar","soy sauce","sugar","salt","maldive fish","roasted curry"],
    "🥛 Dairy & Coconut":      ["coconut milk","coconut","yogurt","milk","butter","ghee","cream","desiccated"],
    "🫙 Pantry":               ["oil","water","stock","sauce","paste","can","dried","baking"],
}

def categorise(name):
    low = name.lower()
    for cat, keywords in INGREDIENT_CATEGORIES.items():
        if any(k in low for k in keywords):
            return cat
    return "🫙 Pantry"

def parse_amount(amount_str, scale):
    """Scale an amount string by `scale` (num_people)."""
    if not amount_str or amount_str in ("to taste", "as needed", "as required"):
        return amount_str
    import re
    m = re.match(r'^([\d./]+)\s*(.*)', amount_str.strip())
    if not m:
        return amount_str
    try:
        num = eval(m.group(1))
        unit = m.group(2).strip()
        scaled = round(num * scale, 2)
        return f"{scaled} {unit}".strip()
    except Exception:
        return amount_str


@cooking_bp.route('/parse-meal-plan', methods=['POST'])
def parse_meal_plan():
    """Parse free-text meal plan using Groq AI"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    try:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": MEAL_PARSE_PROMPT},
                {"role": "user", "content": data['text']}
            ],
            max_tokens=800,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()

        # Extract JSON
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return jsonify({'success': False, 'error': 'Could not parse meal plan from text'}), 200

        meal_plan = json.loads(match.group())
        return jsonify({'success': True, 'meal_plan': meal_plan}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cooking_bp.route('/parse-meal-plan-image', methods=['POST'])
def parse_meal_plan_image():
    """Parse meal plan from an uploaded image using Groq Vision"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    try:
        image_data = file.read()
        b64 = base64.b64encode(image_data).decode('utf-8')
        ext = file.filename.rsplit('.', 1)[-1].lower()
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif'}.get(ext, 'image/jpeg')

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": f"Read this meal plan image carefully.\n\n{MEAL_PARSE_PROMPT}"}
                ]
            }],
            max_tokens=800,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()

        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return jsonify({'success': False, 'error': 'Could not read meal plan from image'}), 200

        meal_plan = json.loads(match.group())
        return jsonify({'success': True, 'meal_plan': meal_plan}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cooking_bp.route('/grocery-from-meals', methods=['POST'])
def grocery_from_meals():
    """
    Build a categorised, scaled grocery list from a list of meal/recipe names.
    Matches against the recipe database, aggregates ingredients, scales by num_people.
    """
    data = request.get_json()
    if not data or 'meals' not in data:
        return jsonify({'error': 'No meals provided'}), 400

    meal_names  = [m.lower().strip() for m in data['meals'] if m]
    num_people  = max(1, int(data.get('num_people', 1)))
    recipes     = _load_recipes()

    # Build lookup: recipe name → recipe dict
    recipe_lookup = {}
    for r in recipes:
        names = r.get('names', {})
        en = (names.get('english', '') if isinstance(names, dict) else str(names)).lower()
        if en:
            recipe_lookup[en] = r
        alt = r.get('name', '').lower()
        if alt:
            recipe_lookup[alt] = r

    # Aggregate ingredients
    agg = {}  # name → {amount_str, recipe_servings}

    matched_recipes = set()
    for meal in meal_names:
        # Fuzzy match
        recipe = recipe_lookup.get(meal)
        if not recipe:
            for key, val in recipe_lookup.items():
                if meal in key or key in meal:
                    recipe = val
                    break
        if not recipe:
            continue

        matched_recipes.add((recipe.get('names', {}) or {}).get('english', '') or recipe.get('name', meal))
        recipe_servings = recipe.get('servings', 4)
        scale = num_people / recipe_servings

        for ing in recipe.get('ingredients', []):
            if isinstance(ing, dict):
                name   = ing.get('name', '')
                amount = ing.get('amount', '')
            else:
                name   = str(ing)
                amount = ''

            if isinstance(name, dict):
                name = name.get('english', '')

            name = name.strip().lower()
            if not name:
                continue

            if name in agg:
                # Already added — just note it appears again (simple approach)
                agg[name]['count'] += 1
            else:
                agg[name] = {
                    'name':            name,
                    'amount':          amount,
                    'recipe_servings': recipe_servings,
                    'scale':           scale,
                    'count':           1,
                }

    # Build categorised output
    categories = {cat: [] for cat in INGREDIENT_CATEGORIES}
    categories["🫙 Pantry"] = categories.get("🫙 Pantry", [])

    for name, info in agg.items():
        cat = categorise(name)
        if cat not in categories:
            categories[cat] = []

        scaled = parse_amount(info['amount'], info['scale'] * info['count'])

        categories[cat].append({
            'name':          name.title(),
            'raw_amount':    info['amount'],
            'scaled_amount': scaled if scaled else f"×{info['count']}",
        })

    # Sort each category alphabetically
    for cat in categories:
        categories[cat].sort(key=lambda x: x['name'])

    # Remove empty categories
    categories = {k: v for k, v in categories.items() if v}

    total_items = sum(len(v) for v in categories.values())

    return jsonify({
        'success':      True,
        'grocery': {
            'categories':    categories,
            'total_items':   total_items,
            'total_meals':   len(matched_recipes),
            'matched_meals': list(matched_recipes),
            'num_people':    num_people,
        },
        'unmatched_meals': [m for m in meal_names if not any(
            m in k or k in m for k in recipe_lookup
        )],
    }), 200