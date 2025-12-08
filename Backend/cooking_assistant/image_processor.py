import os
import io
from google.cloud import vision

def detect_ingredients(image_path):
    """
    Detect ingredients from image using Google Cloud Vision API
    with smart mapping to specific ingredients
    """
    try:
        api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        
        print(f"🔍 DEBUG: API Key exists: {bool(api_key)}")
        print(f"🔍 DEBUG: API Key first 10 chars: {api_key[:10] if api_key else 'None'}...")
        
        if not api_key:
            print("❌ WARNING: No API key found. Using mock data.")
            return get_mock_ingredients()
        
        print(f"✅ API key found! Analyzing image: {image_path}")
        
        # Initialize Vision API client
        client = vision.ImageAnnotatorClient(
            client_options={"api_key": api_key}
        )
        
        # Read the image file
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # 1. Label Detection (general objects)
        label_response = client.label_detection(image=image)
        labels = label_response.label_annotations
        
        # 2. Object Localization (specific objects)
        object_response = client.object_localization(image=image)
        objects = object_response.localized_object_annotations
        
        # 3. Text Detection (for packaged foods)
        text_response = client.text_detection(image=image)
        texts = text_response.text_annotations
        
        # Check for errors
        if label_response.error.message:
            raise Exception(f"API Error: {label_response.error.message}")
        
        # Extract and map ingredients
        detected_items = extract_and_map_ingredients(labels, objects, texts)
        
        # If nothing detected, return fallback
        if not detected_items:
            print("No ingredients detected. Using sample data.")
            return get_mock_ingredients()
        
        return detected_items
        
    except Exception as e:
        print(f"Error in detect_ingredients: {str(e)}")
        return get_mock_ingredients()


def extract_and_map_ingredients(labels, objects, texts):
    """
    Extract ingredients and map generic terms to specific ingredients
    """
    
    # Ingredient mapping dictionary (generic → specific)
    ingredient_mapping = {
        # Vegetables
        'vegetable': ['mixed vegetables'],
        'produce': ['fresh produce'],
        'root vegetable': ['carrot', 'potato', 'radish'],
        'leafy vegetable': ['spinach', 'cabbage', 'lettuce'],
        'allium': ['onion', 'garlic', 'leek'],
        'gourd': ['pumpkin', 'cucumber', 'zucchini'],
        
        # Specific vegetables
        'tomato': ['tomato'],
        'onion': ['onion'],
        'garlic': ['garlic'],
        'ginger': ['ginger'],
        'potato': ['potato'],
        'carrot': ['carrot'],
        'pepper': ['bell pepper', 'chili'],
        'chili': ['green chili', 'red chili'],
        'cucumber': ['cucumber'],
        'cabbage': ['cabbage'],
        'eggplant': ['eggplant', 'brinjal'],
        'pumpkin': ['pumpkin'],
        'beans': ['green beans'],
        'peas': ['peas'],
        'corn': ['corn', 'sweet corn'],
        'mushroom': ['mushroom'],
        'broccoli': ['broccoli'],
        'cauliflower': ['cauliflower'],
        
        # Proteins
        'meat': ['meat'],
        'chicken': ['chicken'],
        'beef': ['beef'],
        'pork': ['pork'],
        'fish': ['fish'],
        'seafood': ['seafood'],
        'shrimp': ['shrimp', 'prawns'],
        'egg': ['egg'],
        'tofu': ['tofu'],
        
        # Grains & Staples
        'rice': ['rice'],
        'wheat': ['wheat flour'],
        'flour': ['flour'],
        'bread': ['bread'],
        'pasta': ['pasta'],
        'noodles': ['noodles'],
        
        # Dairy
        'dairy': ['milk', 'yogurt'],
        'milk': ['milk'],
        'cheese': ['cheese'],
        'butter': ['butter'],
        'cream': ['cream'],
        'yogurt': ['yogurt', 'curd'],
        
        # Spices & Herbs
        'spice': ['spices'],
        'herb': ['herbs'],
        'curry': ['curry powder', 'curry leaves'],
        'turmeric': ['turmeric'],
        'cumin': ['cumin'],
        'coriander': ['coriander'],
        'cinnamon': ['cinnamon'],
        'cardamom': ['cardamom'],
        'chili powder': ['chili powder'],
        'garam masala': ['garam masala'],
        'bay leaf': ['bay leaf'],
        'mint': ['mint'],
        'cilantro': ['cilantro', 'coriander leaves'],
        'basil': ['basil'],
        'parsley': ['parsley'],
        'thyme': ['thyme'],
        'rosemary': ['rosemary'],
        
        # Oils & Condiments
        'oil': ['cooking oil'],
        'coconut': ['coconut', 'coconut milk'],
        'coconut milk': ['coconut milk'],
        'soy sauce': ['soy sauce'],
        'vinegar': ['vinegar'],
        'salt': ['salt'],
        'sugar': ['sugar'],
        'honey': ['honey'],
        
        # Nuts & Seeds
        'nut': ['nuts'],
        'cashew': ['cashew'],
        'peanut': ['peanut'],
        'almond': ['almond'],
        'walnut': ['walnut'],
        'sesame': ['sesame seeds'],
        
        # Fruits
        'fruit': ['fruit'],
        'lemon': ['lemon'],
        'lime': ['lime'],
        'apple': ['apple'],
        'banana': ['banana'],
        'mango': ['mango'],
        'orange': ['orange'],
        'tomato': ['tomato'],  # Technically a fruit
        
        # Lentils & Legumes
        'lentil': ['lentils', 'dhal'],
        'bean': ['beans'],
        'chickpea': ['chickpeas'],
        'red lentil': ['red lentils'],
        'green lentil': ['green lentils'],
    }
    
    # Common ingredients to always include if mentioned
    common_ingredients = {
        'tomato', 'onion', 'garlic', 'ginger', 'potato', 'carrot',
        'chicken', 'rice', 'egg', 'oil', 'salt', 'pepper',
        'chili', 'curry', 'coconut', 'fish', 'beef', 'pork',
        'cucumber', 'cabbage', 'beans', 'peas', 'corn',
        'milk', 'cheese', 'butter', 'flour', 'sugar'
    }
    
    detected_ingredients = set()
    raw_detections = set()
    
    # Process labels
    for label in labels:
        description = label.description.lower().strip()
        raw_detections.add(description)
        
        # Check if it's a common ingredient
        for common in common_ingredients:
            if common in description or description in common:
                detected_ingredients.add(common)
        
        # Map to specific ingredients
        for generic, specifics in ingredient_mapping.items():
            if generic in description:
                detected_ingredients.update(specifics)
    
    # Process objects (usually more specific)
    for obj in objects:
        name = obj.name.lower().strip()
        raw_detections.add(name)
        
        # Check common ingredients
        for common in common_ingredients:
            if common in name or name in common:
                detected_ingredients.add(common)
        
        # Direct mapping
        for generic, specifics in ingredient_mapping.items():
            if generic in name:
                detected_ingredients.update(specifics)
    
    # Process text (for packaged foods)
    if texts and len(texts) > 0:
        detected_text = texts[0].description.lower() if texts else ""
        
        # Look for ingredient keywords in text
        for common in common_ingredients:
            if common in detected_text:
                detected_ingredients.add(common)
    
    # Remove generic terms if we have specific ones
    generic_terms = {'food', 'ingredient', 'produce', 'vegetable', 'fruit', 'meat', 'spice'}
    detected_ingredients = detected_ingredients - generic_terms
    
    # Convert to sorted list
    result = sorted(list(detected_ingredients))
    
    print(f"Raw detections: {raw_detections}")
    print(f"Mapped ingredients: {result}")
    
    return result


def get_mock_ingredients():
    """
    Fallback mock data when API fails or no API key
    """
    return [
        'tomato',
        'onion',
        'garlic',
        'chicken',
        'rice',
        'curry leaves',
        'ginger'
    ]


def test_api_connection():
    """
    Test if Google Cloud Vision API is working
    """
    try:
        api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        
        if not api_key:
            return False, "No API key found in .env file"
        
        client = vision.ImageAnnotatorClient(
            client_options={"api_key": api_key}
        )
        
        return True, "API connection successful!"
        
    except Exception as e:
        return False, f"API connection failed: {str(e)}"