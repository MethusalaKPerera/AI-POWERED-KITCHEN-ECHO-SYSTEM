"""
Gemini API-based Ingredient Detector
Replaces Google Vision API with FREE Gemini API
"""

import google.generativeai as genai
import os
from PIL import Image
import json
import base64
from io import BytesIO

class GeminiIngredientDetector:
    def __init__(self, api_key=None):
        """
        Initialize Gemini API for ingredient detection
        
        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free!
    
    def detect_ingredients(self, image_path=None, image_bytes=None):
        """
        Detect ingredients from an image
        
        Args:
            image_path: Path to image file
            image_bytes: Raw image bytes (alternative to image_path)
        
        Returns:
            dict: {
                'ingredients': [list of detected ingredients],
                'labels': [alternative names/labels],
                'text': [any text found on packages],
                'confidence': overall confidence score
            }
        """
        try:
            # Load image
            if image_path:
                image = Image.open(image_path)
            elif image_bytes:
                image = Image.open(BytesIO(image_bytes))
            else:
                raise ValueError("Either image_path or image_bytes must be provided")
            
            # Create comprehensive prompt for ingredient detection
            prompt = """
Analyze this image and identify ALL food ingredients, items, and products visible.

For each item found, provide:
1. The ingredient/food item name in English
2. Any text visible on packages or labels
3. Estimated quantity if visible
4. Your confidence level (high/medium/low)

IMPORTANT:
- List individual ingredients (e.g., "tomatoes", "onions", "rice")
- Include packaged items (e.g., "coconut milk", "curry powder")
- Read any text on packages carefully
- If you see Sri Lankan/Indian ingredients, identify them properly
- Include spices, condiments, and pantry items

Respond in this EXACT JSON format:
{
    "ingredients": [
        {
            "name": "ingredient name in English",
            "confidence": "high/medium/low",
            "quantity": "approximate quantity if visible",
            "package_text": "any text visible on package"
        }
    ],
    "package_labels": ["text found on packages"],
    "notes": "any additional observations"
}
"""
            
            # Generate content with image
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            result_text = response.text
            
            # Try to extract JSON from response
            try:
                # Remove markdown code blocks if present
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                result = self._parse_text_response(result_text)
            
            # Format response to match your existing system
            formatted_response = {
                'ingredients': [item['name'] for item in result.get('ingredients', [])],
                'labels': result.get('package_labels', []),
                'text': result.get('package_labels', []),
                'confidence': self._calculate_overall_confidence(result.get('ingredients', [])),
                'detailed_items': result.get('ingredients', []),
                'raw_response': result_text
            }
            
            return formatted_response
            
        except Exception as e:
            print(f"Error detecting ingredients: {str(e)}")
            return {
                'ingredients': [],
                'labels': [],
                'text': [],
                'confidence': 0,
                'error': str(e)
            }
    
    def detect_ingredients_multilingual(self, image_path=None, image_bytes=None, languages=['english', 'sinhala', 'tamil']):
        """
        Detect ingredients with multilingual support
        Perfect for Sri Lankan products with Sinhala/Tamil text
        """
        try:
            if image_path:
                image = Image.open(image_path)
            elif image_bytes:
                image = Image.open(BytesIO(image_bytes))
            else:
                raise ValueError("Either image_path or image_bytes must be provided")
            
            lang_instruction = ", ".join(languages)
            
            prompt = f"""
Analyze this image and identify ALL food ingredients and text in {lang_instruction}.

TASKS:
1. Identify all visible ingredients/food items
2. Read ALL text on packages (in English, Sinhala සිංහල, or Tamil தமிழ்)
3. Translate ingredient names to English if they're in other languages

Respond in JSON format:
{{
    "ingredients": [
        {{
            "name_english": "ingredient name",
            "name_sinhala": "සිංහල නම if visible",
            "name_tamil": "தமிழ் பெயர் if visible",
            "confidence": "high/medium/low"
        }}
    ],
    "package_text": {{
        "english": ["text in English"],
        "sinhala": ["text in Sinhala"],
        "tamil": ["text in Tamil"]
    }}
}}
"""
            
            response = self.model.generate_content([prompt, image])
            result_text = response.text
            
            # Parse JSON response
            try:
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                result = json.loads(result_text)
            except:
                result = {'ingredients': [], 'package_text': {}}
            
            return result
            
        except Exception as e:
            print(f"Error in multilingual detection: {str(e)}")
            return {'ingredients': [], 'package_text': {}, 'error': str(e)}
    
    def _parse_text_response(self, text):
        """Parse text response when JSON parsing fails"""
        lines = text.strip().split('\n')
        ingredients = []
        labels = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('Note'):
                # Try to extract ingredient names
                if any(keyword in line.lower() for keyword in ['ingredient', 'item', 'food']):
                    continue
                # Extract actual ingredients
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    ingredient_name = line.lstrip('-•* ').split(':')[0].strip()
                    if ingredient_name:
                        ingredients.append({
                            'name': ingredient_name,
                            'confidence': 'medium',
                            'quantity': '',
                            'package_text': ''
                        })
        
        return {
            'ingredients': ingredients,
            'package_labels': labels,
            'notes': text
        }
    
    def _calculate_overall_confidence(self, ingredients):
        """Calculate overall confidence score"""
        if not ingredients:
            return 0
        
        confidence_map = {'high': 0.9, 'medium': 0.7, 'low': 0.5}
        scores = [confidence_map.get(item.get('confidence', 'medium'), 0.7) for item in ingredients]
        
        return sum(scores) / len(scores) if scores else 0


# Flask route integration example
def create_ingredient_detection_route(app, detector):
    """
    Add this to your Flask app.py
    """
    from flask import request, jsonify
    
    @app.route('/api/detect-ingredients', methods=['POST'])
    def detect_ingredients():
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            image_file = request.files['image']
            image_bytes = image_file.read()
            
            # Detect ingredients using Gemini
            result = detector.detect_ingredients(image_bytes=image_bytes)
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/detect-ingredients-multilingual', methods=['POST'])
    def detect_ingredients_multilingual():
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            image_file = request.files['image']
            image_bytes = image_file.read()
            
            # Detect with multilingual support
            result = detector.detect_ingredients_multilingual(image_bytes=image_bytes)
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    # Test the detector
    print("Testing Gemini Ingredient Detector...")
    
    # Initialize detector
    detector = GeminiIngredientDetector()
    
    print("✅ Detector initialized successfully!")
    print("\nTo use in your Flask app:")
    print("1. Set GEMINI_API_KEY environment variable")
    print("2. Import: from gemini_ingredient_detector import GeminiIngredientDetector")
    print("3. Initialize: detector = GeminiIngredientDetector()")
    print("4. Use: result = detector.detect_ingredients(image_path='path/to/image.jpg')")