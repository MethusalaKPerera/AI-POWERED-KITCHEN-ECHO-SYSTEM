from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image

cooking_bp = Blueprint('cooking', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cooking_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Upload and analyze ingredient image"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        # TODO Day 2: Call Google Vision API
        # For now, return mock data
        detected_ingredients = [
            'tomato',
            'onion', 
            'chicken',
            'rice',
            'curry leaves',
            'garlic'
        ]
        
        return jsonify({
            'success': True,
            'ingredients': detected_ingredients,
            'message': 'Image analyzed successfully (mock data)',
            'image_path': filepath
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error processing image: {str(e)}'
        }), 500


@cooking_bp.route('/search-recipes', methods=['POST'])
def search_recipes():
    """Search recipes by ingredients"""
    data = request.get_json()
    
    if not data or 'ingredients' not in data:
        return jsonify({'error': 'No ingredients provided'}), 400
    
    ingredients = data['ingredients']
    
    # TODO Day 3-5: Implement RAG model + ML matching
    # Mock recipes for now
    mock_recipes = [
        {
            'id': 1,
            'name': 'Sri Lankan Chicken Curry',
            'cuisine': 'Sri Lankan',
            'source': 'RAG Model',
            'match_score': 95,
            'matched_ingredients': ['chicken', 'curry leaves', 'onion', 'garlic'],
            'missing_ingredients': ['coconut milk', 'turmeric'],
            'cooking_time': '45 mins',
            'difficulty': 'Medium',
            'servings': 4
        },
        {
            'id': 2,
            'name': 'Chicken Fried Rice',
            'cuisine': 'Asian',
            'source': '1M+ Database',
            'match_score': 88,
            'matched_ingredients': ['chicken', 'rice', 'onion', 'garlic'],
            'missing_ingredients': ['soy sauce', 'vegetables', 'egg'],
            'cooking_time': '20 mins',
            'difficulty': 'Easy',
            'servings': 2
        },
        {
            'id': 3,
            'name': 'Tomato Rice',
            'cuisine': 'Indian',
            'source': '1M+ Database',
            'match_score': 82,
            'matched_ingredients': ['rice', 'tomato', 'onion'],
            'missing_ingredients': ['spices', 'oil'],
            'cooking_time': '30 mins',
            'difficulty': 'Easy',
            'servings': 3
        }
    ]
    
    return jsonify({
        'success': True,
        'recipes': mock_recipes,
        'total_found': len(mock_recipes),
        'search_query': ingredients
    }), 200


@cooking_bp.route('/generate-grocery-list', methods=['POST'])
def generate_grocery_list():
    """Generate grocery list from meal plan"""
    data = request.get_json()
    
    if not data or 'meal_plan' not in data:
        return jsonify({'error': 'No meal plan provided'}), 400
    
    meal_plan = data['meal_plan']
    num_people = data.get('num_people', 1)
    
    # TODO Day 6: Implement grocery aggregation
    # Mock grocery list
    mock_grocery_list = {
        'vegetables': [
            {'item': 'Onions', 'quantity': 500 * num_people, 'unit': 'g'},
            {'item': 'Tomatoes', 'quantity': 750 * num_people, 'unit': 'g'},
            {'item': 'Garlic', 'quantity': 100 * num_people, 'unit': 'g'},
        ],
        'protein': [
            {'item': 'Chicken', 'quantity': 1.5 * num_people, 'unit': 'kg'},
        ],
        'grains': [
            {'item': 'Rice', 'quantity': 2 * num_people, 'unit': 'kg'},
        ],
        'spices': [
            {'item': 'Curry leaves', 'quantity': 50 * num_people, 'unit': 'g'},
            {'item': 'Turmeric', 'quantity': 20 * num_people, 'unit': 'g'},
        ],
        'dairy': [
            {'item': 'Coconut milk', 'quantity': 400 * num_people, 'unit': 'ml'},
        ]
    }
    
    return jsonify({
        'success': True,
        'grocery_list': mock_grocery_list,
        'total_items': sum(len(items) for items in mock_grocery_list.values()),
        'num_people': num_people
    }), 200