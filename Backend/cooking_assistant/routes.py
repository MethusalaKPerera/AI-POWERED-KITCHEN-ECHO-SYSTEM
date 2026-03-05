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

# ── Groq client ─────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# ── Ingredient categories ───────────────────────────────
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
  "monday": {"breakfast": "", "lunch": "", "dinner": ""},
  "tuesday": {"breakfast": "", "lunch": "", "dinner": ""},
  "wednesday": {"breakfast": "", "lunch": "", "dinner": ""},
  "thursday": {"breakfast": "", "lunch": "", "dinner": ""},
  "friday": {"breakfast": "", "lunch": "", "dinner": ""},
  "saturday": {"breakfast": "", "lunch": "", "dinner": ""},
  "sunday": {"breakfast": "", "lunch": "", "dinner": ""}
}

Leave fields empty if not mentioned.
"""

# ───────────────── Helpers ─────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    unit = match.group(2).strip()

    try:
        if '/' in num_str:
            num = eval(num_str)
        else:
            num = float(num_str)

        scaled = round(num * scale, 2)
        return {'value': scaled, 'unit': unit}

    except:
        return {'value': 0, 'unit': amount_str}


def _load_recipes():
    data_dir = os.path.join(os.path.dirname(__file__), 'rag', 'data')

    for fname in ['recipes_all_merged.json','new_200_recipes.json','recipe_database.json']:
        fp = os.path.join(data_dir, fname)

        if os.path.exists(fp):
            with open(fp,'r',encoding='utf-8') as f:
                data=json.load(f)

            return data.get('recipes',[]) if isinstance(data,dict) else data

    return []


def _build_recipe_lookup(recipes):
    lookup={}

    for r in recipes:
        name=(r.get('name') or '').lower().strip()
        if name:
            lookup[name]=r

    return lookup


# ───────────────── Routes ─────────────────

@cooking_bp.route('/analyze-image', methods=['POST'])
def analyze_image():

    if 'image' not in request.files:
        return jsonify({'error':'No image file provided'}),400

    file=request.files['image']

    if file.filename=='':
        return jsonify({'error':'No file selected'}),400

    if not allowed_file(file.filename):
        return jsonify({'error':'Invalid file type'}),400

    try:

        filename=secure_filename(file.filename)

        upload_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)),'uploads')
        os.makedirs(upload_dir,exist_ok=True)

        filepath=os.path.join(upload_dir,filename)
        file.save(filepath)

        from image_processor import detect_ingredients

        detected=detect_ingredients(filepath)

        return jsonify({
            'success':True,
            'ingredients':detected,
            'total_detected':len(detected)
        })

    except Exception as e:
        return jsonify({'error':str(e)}),500


@cooking_bp.route('/search-recipes', methods=['POST'])
def search_recipes():

    data=request.get_json()

    if not data or 'ingredients' not in data:
        return jsonify({'error':'No ingredients provided'}),400

    user_ingredients=[i.lower().strip() for i in data['ingredients']]

    recipes=_load_recipes()

    results=[]

    for recipe in recipes:

        recipe_ings=[(ing.get('name') if isinstance(ing,dict) else str(ing)).lower()
                     for ing in recipe.get('ingredients',[])]

        matched=[ui for ui in user_ingredients if any(ui in ri for ri in recipe_ings)]

        if not recipe_ings:
            continue

        score=round((len(matched)/len(recipe_ings))*100)

        if score==0:
            continue

        results.append({
            'id':recipe.get('id'),
            'name':recipe.get('name'),
            'match_score':score,
            'matched_ingredients':matched,
            'ingredients':recipe.get('ingredients'),
            'servings':recipe.get('servings',4)
        })

    results.sort(key=lambda x:x['match_score'],reverse=True)

    return jsonify({'success':True,'recipes':results[:12]})


@cooking_bp.route('/parse-meal-plan', methods=['POST'])
def parse_meal_plan():

    data=request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error':'No text provided'}),400

    try:

        response=groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role":"system","content":MEAL_PARSE_PROMPT},
                {"role":"user","content":data['text']}
            ],
            temperature=0.1,
            max_tokens=800
        )

        raw=response.choices[0].message.content.strip()

        match=re.search(r'\{.*\}',raw,re.DOTALL)

        if not match:
            return jsonify({'success':False}),200

        return jsonify({
            'success':True,
            'meal_plan':json.loads(match.group())
        })

    except Exception as e:
        return jsonify({'success':False,'error':str(e)})


@cooking_bp.route('/parse-meal-plan-image', methods=['POST'])
def parse_meal_plan_image():

    if 'image' not in request.files:
        return jsonify({'error':'No image provided'}),400

    file=request.files['image']

    try:

        b64=base64.b64encode(file.read()).decode('utf-8')

        response=groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role":"user",
                "content":[
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}},
                    {"type":"text","text":MEAL_PARSE_PROMPT}
                ]
            }],
            max_tokens=800
        )

        raw=response.choices[0].message.content.strip()

        match=re.search(r'\{.*\}',raw,re.DOTALL)

        if not match:
            return jsonify({'success':False}),200

        return jsonify({
            'success':True,
            'meal_plan':json.loads(match.group())
        })

    except Exception as e:
        return jsonify({'success':False,'error':str(e)})


@cooking_bp.route('/grocery-from-meals', methods=['POST'])
def grocery_from_meals():

    data=request.get_json()

    if not data or 'meals' not in data:
        return jsonify({'error':'No meals provided'}),400

    meal_names=[m.lower().strip() for m in data['meals']]

    num_people=max(1,int(data.get('num_people',1)))

    recipes=_load_recipes()

    lookup=_build_recipe_lookup(recipes)

    agg={}

    for meal in meal_names:

        recipe=lookup.get(meal)

        if not recipe:
            continue

        servings=recipe.get('servings',4)

        for ing in recipe.get('ingredients',[]):

            name=(ing.get('name') if isinstance(ing,dict) else str(ing)).lower()

            amount=ing.get('amount','') if isinstance(ing,dict) else ''

            scaled=_scale_amount(amount,num_people,servings)

            if name not in agg:
                agg[name]=scaled
            else:
                agg[name]['value']+=scaled['value']

    categories={cat:[] for cat in INGREDIENT_CATEGORIES}

    for name,data in agg.items():

        cat=_categorise(name)

        categories[cat].append({
            'name':name.title(),
            'amount':f"{data['value']} {data['unit']}".strip()
        })

    categories={k:v for k,v in categories.items() if v}

    return jsonify({
        'success':True,
        'grocery':categories
    })