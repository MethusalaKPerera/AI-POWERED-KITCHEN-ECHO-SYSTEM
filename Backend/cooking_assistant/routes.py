from dotenv import load_dotenv
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

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

# ── RAG System (singleton) ────────────────────────────────────────────────────
_rag_system = None

def _get_rag():
    global _rag_system
    if _rag_system is None:
        try:
            from rag.rag_system import RAGSystem
            data_dir    = _os.path.join(_os.path.dirname(__file__), 'rag', 'data')
            _rag_system = RAGSystem(data_dir)
            print("[RAG] ✓ RAG System loaded successfully")
        except Exception as e:
            print(f"[RAG] ✗ Failed to load RAG system: {e}")
            _rag_system = None
    return _rag_system

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

    candidates = [
        _os.path.join(data_dir, 'recipes_all_merged.json'),
        _os.path.join(data_dir, 'new_200_recipes.json'),
        _os.path.join(data_dir, 'recipes', 'recipe_database.json'),
        _os.path.join(data_dir, 'recipe_database.json'),
    ]

    for fp in candidates:
        if _os.path.exists(fp):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                recipes = data.get('recipes', []) if isinstance(data, dict) else data
                print(f"[routes] ✓ Loaded {len(recipes)} recipes from {_os.path.basename(fp)}")
                return recipes
            except Exception as e:
                print(f"[routes] Error loading {fp}: {e}")

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


def _clean_ing_name(raw_name) -> str:
    """
    Clean ingredient name the same way semantic_search does.
    Handles: '1 kg chicken, cut into pieces' → 'chicken'
    """
    s = str(raw_name).strip()
    s = re.sub(
        r'^\d+[\d./]*\s*(g|kg|mg|ml|l|cup|cups|tsp|tbsp|oz|lb|piece|pieces|'
        r'can|tin|medium|large|small|bunch|handful|cloves?|clove|inch|cm|'
        r'slice|slices|stalk|stalks|sprig|sprigs|pinch|drop|drops)?\s*',
        '', s, flags=re.IGNORECASE
    )
    if ',' in s:
        s = s.split(',')[0].strip()
    s = re.sub(
        r'\s+(sliced|diced|chopped|minced|grated|crushed|cubed|cut|peeled|'
        r'washed|cooked|raw|fresh|dried|ground|whole|boneless|skinless|'
        r'boiled|fried|finely|roughly|thinly|thickly|cleaned|rinsed)\b.*$',
        '', s, flags=re.IGNORECASE
    )
    return s.strip().lower()


def _keyword_search(user_ingredients, recipes, top_k=12):
    """Fallback keyword-based recipe search."""
    results = []

    for recipe in recipes:
        en_name    = _get_recipe_name(recipe)
        name_lower = en_name.lower()

        # Skip bad placeholder recipes
        bad = ['page 1', 'page 2', '---', 'placeholder']
        if any(b in name_lower for b in bad):
            continue

        recipe_ings     = []
        has_placeholder = False

        for ing in recipe.get('ingredients', []):
            raw_name = ing.get('name', '') if isinstance(ing, dict) else str(ing)
            if isinstance(raw_name, dict):
                raw_name = raw_name.get('english', '')

            if "ingredients to be added" in str(raw_name).lower():
                has_placeholder = True
                break

            clean = _clean_ing_name(raw_name)
            if clean:
                recipe_ings.append(clean)

        method = recipe.get('method', '') or recipe.get('instructions', '')
        if not method or "instructions to be added" in method.lower() \
                or "detailed cooking instructions" in method.lower():
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
            'recommendation':      '',
        })

    results.sort(key=lambda x: (
        any(
            p in x['name'].lower() and any(
                _ingredient_matches(p, ui) for ui in user_ingredients
            )
            for p in MAIN_PROTEINS
        ),
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
            return jsonify({
                'success': False,
                'error':   result.get('error', 'Failed to detect ingredients')
            })

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
    method_used      = 'keyword-fallback'
    recommendation   = ''
    results          = []
    recipes          = _load_recipes()

    print(f"[search] {len(user_ingredients)} ingredients, {len(recipes)} recipes in DB")

    # ── Step 1: Use sbert_matcher for recipe search ───────────────────────────
    try:
        from sbert_matcher import sbert_search_recipes
        results     = sbert_search_recipes(user_ingredients, recipes, top_k=12)
        method_used = 'sentence-bert'
        print(f"[SBERT] ✓ {len(results)} recipes found")
        if results:
            print(f"[SBERT] Top: {results[0].get('name')} ({results[0].get('match_score')}%)")
    except Exception as e:
        print(f"[SBERT] ✗ {e} — falling back to keyword")
        results     = _keyword_search(user_ingredients, recipes)
        method_used = 'keyword-fallback'

    # ── Step 2: Use RAG for generating recommendation text only ──────────────
    if results:
        rag = _get_rag()
        if rag:
            try:
                recommendation = rag.generator.generate_recommendation(
                    user_ingredients     = user_ingredients,
                    retrieved_recipes    = results[:5],
                    user_preferences     = None,
                    conversation_history = None,
                )
                method_used = 'rag-sbert'
                print(f"[RAG] ✓ Recommendation generated")
            except Exception as e:
                print(f"[RAG] recommendation failed: {e}")

    return jsonify({
        'success':        True,
        'recipes':        results,
        'total_found':    len(results),
        'database_size':  len(recipes),
        'search_method':  method_used,
        'recommendation': recommendation,
    })


@cooking_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_message     = data.get('message', '')
    user_ingredients = [i.lower().strip() for i in data.get('ingredients', [])]

    rag = _get_rag()
    if not rag:
        return jsonify({
            'success':        False,
            'error':          'RAG system not available',
            'recommendation': 'Please try again later.',
        }), 500

    try:
        result = rag.chat(
            user_message     = user_message,
            user_ingredients = user_ingredients if user_ingredients else None,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cooking_bp.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    for r in _load_recipes():
        if r.get('id') == recipe_id:
            return jsonify({'success': True, 'recipe': r}), 200
    return jsonify({'error': 'Recipe not found'}), 404


@cooking_bp.route('/like-recipe', methods=['POST'])
def like_recipe():
    data = request.get_json()
    rag  = _get_rag()
    if rag and data:
        rag.like_recipe(data.get('id', ''), data.get('name', ''))
    return jsonify({'success': True})


@cooking_bp.route('/reject-recipe', methods=['POST'])
def reject_recipe():
    data = request.get_json()
    rag  = _get_rag()
    if rag and data:
        rag.reject_recipe(
            data.get('id', ''),
            data.get('name', ''),
            data.get('reason', ''),
        )
    return jsonify({'success': True})


@cooking_bp.route('/set-preference', methods=['POST'])
def set_preference():
    data = request.get_json()
    rag  = _get_rag()
    if rag and data:
        rag.set_preference(data.get('key', ''), data.get('value', ''))
    return jsonify({'success': True})


@cooking_bp.route('/ingest-cookbooks', methods=['POST'])
def ingest_cookbooks():
    data          = request.get_json() or {}
    cookbooks_dir = data.get(
        'cookbooks_dir',
        _os.path.join(_os.path.dirname(__file__), 'cookbooks')
    )
    rag = _get_rag()
    if not rag:
        return jsonify({'success': False, 'error': 'RAG system not available'}), 500
    try:
        result = rag.ingest_cookbooks(cookbooks_dir)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cooking_bp.route('/rag-status', methods=['GET'])
def rag_status():
    rag = _get_rag()

    if not rag:
        return jsonify({
            'rag_loaded':   False,
            'status':       '❌ RAG system not available',
            'sbert_loaded': False,
            'generation':   False,
            'memory':       False,
        })

    sbert_ok = False
    try:
        rag.semantic_search.search(
            ['chicken', 'onion'],
            rag.retriever.get_all_recipes()[:5],
            top_k=1
        )
        sbert_ok = True
    except Exception:
        pass

    gen_ok = False
    try:
        from rag.generation.response_generator import ResponseGenerator
        gen_ok = True
    except Exception:
        pass

    db_stats = rag.get_database_stats()

    return jsonify({
        'rag_loaded':   True,
        'status':       '✅ Full RAG pipeline is active',
        'sbert_loaded': sbert_ok,
        'generation':   gen_ok,
        'memory':       True,
        'database':     db_stats,
    })


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
        mime = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png',  'gif':  'image/gif'
        }.get(ext, 'image/jpeg')

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": f"Read this meal plan image carefully.\n\n{MEAL_PARSE_PROMPT}"},
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

            name = _clean_ing_name(raw_name)
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