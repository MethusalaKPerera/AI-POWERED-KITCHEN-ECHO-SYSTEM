"""
Translation Engine - On-demand translation with curated dictionary + Google Translate fallback
"""
from flask import Blueprint, request, jsonify
import json
import os

translation_bp = Blueprint('translation', __name__)

# Load curated translations
_curated = {}
_curated_path = os.path.join(os.path.dirname(__file__), 'rag', 'data', 'curated_translations.json')
if os.path.exists(_curated_path):
    try:
        with open(_curated_path, 'r', encoding='utf-8') as f:
            _curated = json.load(f)
    except Exception:
        pass

# Common ingredient translations (built-in fallback)
_ingredient_dict = {
    "chicken": {"si": "කුකුල් මස්", "ta": "கோழி"},
    "rice": {"si": "සහල්", "ta": "அரிசி"},
    "onion": {"si": "ලූනු", "ta": "வெங்காயம்"},
    "garlic": {"si": "සුදුලූණු", "ta": "பூண்டு"},
    "ginger": {"si": "ඉඟුරු", "ta": "இஞ்சி"},
    "chili": {"si": "මිරිස්", "ta": "மிளகாய்"},
    "coconut milk": {"si": "පොල්කිරි", "ta": "தேங்காய் பால்"},
    "coconut": {"si": "පොල්", "ta": "தேங்காய்"},
    "curry powder": {"si": "කරි කුඩු", "ta": "கறி பொடி"},
    "turmeric": {"si": "කහ", "ta": "மஞ்சள்"},
    "curry leaves": {"si": "කරපිංචා", "ta": "கருவேப்பிலை"},
    "salt": {"si": "ලුණු", "ta": "உப்பு"},
    "oil": {"si": "තෙල්", "ta": "எண்ணெய்"},
    "tomato": {"si": "තක්කාලි", "ta": "தக்காளி"},
    "potato": {"si": "අල", "ta": "உருளைக்கிழங்கு"},
    "fish": {"si": "මාළු", "ta": "மீன்"},
    "egg": {"si": "බිත්තර", "ta": "முட்டை"},
    "lentils": {"si": "පරිප්පු", "ta": "பருப்பு"},
    "cinnamon": {"si": "කුරුඳු", "ta": "இலவங்கப்பட்டை"},
    "black pepper": {"si": "ගම්මිරිස්", "ta": "மிளகு"},
    "mustard seeds": {"si": "අබ ඇට", "ta": "கடுகு"},
    "banana": {"si": "කෙසෙල්", "ta": "வாழைப்பழம்"},
    "mango": {"si": "අඹ", "ta": "மாம்பழம்"},
    "sugar": {"si": "සීනි", "ta": "சர்க்கரை"},
    "water": {"si": "වතුර", "ta": "தண்ணீர்"},
    "flour": {"si": "පිටි", "ta": "மாவு"},
    "butter": {"si": "බටර්", "ta": "வெண்ணெய்"},
    "milk": {"si": "කිරි", "ta": "பால்"},
    "prawn": {"si": "ඉස්සෝ", "ta": "இறால்"},
    "crab": {"si": "කකුළුවෝ", "ta": "நண்டு"},
    "mutton": {"si": "එළු මස්", "ta": "ஆட்டிறைச்சி"},
    "beef": {"si": "හරක් මස්", "ta": "மாட்டிறைச்சி"},
    "pumpkin": {"si": "වට්ටක්කා", "ta": "பூசணி"},
    "eggplant": {"si": "වම්බටු", "ta": "கத்தரிக்காய்"},
    "spinach": {"si": "නිවිති", "ta": "கீரை"},
    "carrot": {"si": "කැරට්", "ta": "கேரட்"},
    "beans": {"si": "බෝංචි", "ta": "பீன்ஸ்"},
    "cabbage": {"si": "ගෝවා", "ta": "முட்டைகோஸ்"},
    "cashew": {"si": "කජු", "ta": "முந்திரி"},
    "jaggery": {"si": "හකුරු", "ta": "வெல்லம்"},
    "treacle": {"si": "පැණි", "ta": "பாகு"},
}

# UI translations
_ui_dict = {
    "Cooking Assistant": {"si": "ඉවුම් පිවුම් සහායක", "ta": "சமையல் உதவி"},
    "Ingredients": {"si": "අමුද්‍රව්‍ය", "ta": "பொருட்கள்"},
    "Method": {"si": "ක්‍රමය", "ta": "முறை"},
    "Tips": {"si": "ඉඟි", "ta": "குறிப்புகள்"},
    "Recipe": {"si": "වට්ටෝරුව", "ta": "சமையல் குறிப்பு"},
    "Search": {"si": "සොයන්න", "ta": "தேடு"},
    "Upload Image": {"si": "පින්තූරය උඩුගත කරන්න", "ta": "படத்தை பதிவேற்று"},
    "Meal Planner": {"si": "ආහාර සැලසුම්කරු", "ta": "உணவு திட்டமிடல்"},
    "Grocery List": {"si": "සිල්ලර ලැයිස්තුව", "ta": "மளிகை பட்டியல்"},
    "Waste Tracker": {"si": "අපද්‍රව්‍ය නිරීක්ෂක", "ta": "கழிவு கண்காணிப்பு"},
}

def _lookup(text, target):
    """Look up in dictionaries"""
    key = text.lower().strip()
    lang = "si" if target == "si" else "ta"
    
    # Check curated first
    if key in _curated:
        return _curated[key].get(lang, None)
    
    # Check ingredient dict
    if key in _ingredient_dict:
        return _ingredient_dict[key].get(lang, None)
    
    # Check UI dict
    if text in _ui_dict:
        return _ui_dict[text].get(lang, None)
    
    return None

@translation_bp.route('/translate', methods=['POST'])
def translate():
    """On-demand translation endpoint"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    target = data.get('target', 'si')  # 'si' for Sinhala, 'ta' for Tamil
    
    # Try curated dictionary first
    curated_result = _lookup(text, target)
    if curated_result:
        return jsonify({
            'success': True,
            'original': text,
            'translated': curated_result,
            'target_language': target,
            'source': 'curated',
            'confidence': 0.98
        }), 200
    
    # Fallback to Google Translate
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, dest=target)
        return jsonify({
            'success': True,
            'original': text,
            'translated': result.text,
            'target_language': target,
            'source': 'google_translate',
            'confidence': 0.75
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'original': text,
            'translated': text,
            'target_language': target,
            'source': 'fallback',
            'confidence': 0.0,
            'error': str(e)
        }), 200


@translation_bp.route('/dictionary', methods=['GET'])
def get_dictionary():
    """Get the full ingredient translation dictionary"""
    return jsonify({
        'success': True,
        'ingredients': _ingredient_dict,
        'ui_terms': _ui_dict,
        'curated_count': len(_curated),
        'total_entries': len(_ingredient_dict) + len(_ui_dict) + len(_curated)
    }), 200
