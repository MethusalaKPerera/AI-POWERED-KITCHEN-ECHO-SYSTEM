"""
Flask App Integration Example - Gemini API
Drop this code into your existing app.py or cooking_assistant app
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from gemini_ingredient_detector import GeminiIngredientDetector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize Gemini detector once at startup
# This is more efficient than creating new detector for each request
try:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print("⚠️  Warning: GEMINI_API_KEY not set in .env file")
        print("📝 Add this line to your .env: GEMINI_API_KEY=your_actual_key")
    
    gemini_detector = GeminiIngredientDetector(api_key=GEMINI_API_KEY)
    print("✅ Gemini Ingredient Detector initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize Gemini detector: {str(e)}")
    gemini_detector = None


# ============================================================================
# ROUTE 1: Basic Ingredient Detection (Drop-in replacement)
# ============================================================================

@app.route('/api/detect-ingredients', methods=['POST'])
def detect_ingredients():
    """
    Detect ingredients from uploaded image
    
    Request:
        - Form data with 'image' file
    
    Response:
        {
            "ingredients": ["tomatoes", "onions", "curry leaves"],
            "labels": ["Prima Coconut Milk"],
            "text": ["Prima", "Coconut Milk", "400ml"],
            "confidence": 0.85
        }
    """
    try:
        # Check if detector is initialized
        if not gemini_detector:
            return jsonify({
                'error': 'Gemini API not configured. Please set GEMINI_API_KEY in .env'
            }), 500
        
        # Check if image is provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        
        # Validate file
        if image_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Read image bytes
        image_bytes = image_file.read()
        
        # Detect ingredients using Gemini
        result = gemini_detector.detect_ingredients(image_bytes=image_bytes)
        
        # Check for errors
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'ingredients': [],
                'confidence': 0
            }), 500
        
        # Return successful result
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}',
            'ingredients': [],
            'confidence': 0
        }), 500


# ============================================================================
# ROUTE 2: Multilingual Detection (Sri Lankan Products)
# ============================================================================

@app.route('/api/detect-ingredients-multilingual', methods=['POST'])
def detect_ingredients_multilingual():
    """
    Detect ingredients with Sinhala, Tamil & English support
    Perfect for Sri Lankan products with local language labels
    
    Response:
        {
            "ingredients": [
                {
                    "name_english": "coconut milk",
                    "name_sinhala": "පොල් කිරි",
                    "name_tamil": "தேங்காய் பால்",
                    "confidence": "high"
                }
            ],
            "package_text": {
                "english": ["Prima", "Coconut Milk"],
                "sinhala": ["පොල් කිරි"],
                "tamil": ["தேங்காய் பால்"]
            }
        }
    """
    try:
        if not gemini_detector:
            return jsonify({'error': 'Gemini API not configured'}), 500
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image_bytes = image_file.read()
        
        # Get languages from request (optional)
        languages = request.form.get('languages', 'english,sinhala,tamil').split(',')
        
        # Detect with multilingual support
        result = gemini_detector.detect_ingredients_multilingual(
            image_bytes=image_bytes,
            languages=languages
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ROUTE 3: Health Check & API Status
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Check if API is running and Gemini is configured
    """
    status = {
        'status': 'running',
        'gemini_configured': gemini_detector is not None,
        'api_version': 'v2.0-gemini'
    }
    
    return jsonify(status), 200


@app.route('/api/detector-info', methods=['GET'])
def detector_info():
    """
    Get information about the current detector configuration
    """
    if not gemini_detector:
        return jsonify({
            'configured': False,
            'message': 'Gemini API not configured. Set GEMINI_API_KEY in .env'
        }), 200
    
    return jsonify({
        'configured': True,
        'detector': 'Gemini 1.5 Flash',
        'features': [
            'Ingredient detection',
            'OCR/Text reading',
            'Multilingual support (English, Sinhala, Tamil)',
            'Package label reading',
            'Confidence scoring'
        ],
        'limits': {
            'free_tier': '15 requests per minute',
            'cost': 'FREE'
        }
    }), 200


# ============================================================================
# ROUTE 4: Test Detection (for development)
# ============================================================================

@app.route('/api/test-detection', methods=['GET'])
def test_detection():
    """
    Simple test endpoint to verify Gemini is working
    """
    if not gemini_detector:
        return jsonify({
            'success': False,
            'message': 'Gemini API not configured'
        }), 500
    
    try:
        # Test with a simple text prompt (no image needed)
        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("List 3 common vegetables. Just the names.")
        
        return jsonify({
            'success': True,
            'message': 'Gemini API is working!',
            'test_response': response.text
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Test failed: {str(e)}'
        }), 500


# ============================================================================
# INTEGRATION WITH YOUR EXISTING RECIPE MATCHER
# ============================================================================

def integrate_with_recipe_matcher(detected_ingredients):
    """
    Example: Integrate detected ingredients with your recipe matching system
    
    This is how you'd connect the ingredient detection to your existing
    recipe recommendation/matching logic
    """
    # Your existing imports
    # from recipe_matcher import find_matching_recipes
    # from chromadb_handler import search_recipes
    
    # Extract ingredient names
    ingredient_names = detected_ingredients.get('ingredients', [])
    
    # Example: Search recipes using detected ingredients
    # matching_recipes = find_matching_recipes(ingredient_names)
    # return matching_recipes
    
    return {
        'detected_ingredients': ingredient_names,
        'message': 'Connect this to your recipe matcher'
    }


# ============================================================================
# MAIN APP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🍳 AI-Powered Kitchen Echo System - Gemini Edition")
    print("=" * 60)
    
    if gemini_detector:
        print("✅ Gemini Detector: READY")
    else:
        print("⚠️  Gemini Detector: NOT CONFIGURED")
        print("   Set GEMINI_API_KEY in your .env file")
    
    print("\n📍 Available Endpoints:")
    print("   POST /api/detect-ingredients")
    print("   POST /api/detect-ingredients-multilingual")
    print("   GET  /api/health")
    print("   GET  /api/detector-info")
    print("   GET  /api/test-detection")
    
    print("\n🌐 Starting Flask server...")
    print("=" * 60)
    print()
    
    # Run the app
    app.run(
        debug=True,
        host='0.0.0.0',  # Accessible from network
        port=5000
    )


# ============================================================================
# USAGE EXAMPLE FROM FRONTEND
# ============================================================================
"""
// React/JavaScript frontend example
async function detectIngredients(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    try {
        const response = await fetch('http://localhost:5000/api/detect-ingredients', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        console.log('Detected ingredients:', result.ingredients);
        console.log('Confidence:', result.confidence);
        console.log('Package text:', result.text);
        
        return result;
    } catch (error) {
        console.error('Detection failed:', error);
    }
}

// For multilingual detection
async function detectIngredientsMultilingual(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('languages', 'english,sinhala,tamil');
    
    const response = await fetch('http://localhost:5000/api/detect-ingredients-multilingual', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
"""