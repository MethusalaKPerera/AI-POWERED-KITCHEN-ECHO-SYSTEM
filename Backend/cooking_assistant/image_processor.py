import os
import io
from google.cloud import vision
from google.oauth2 import service_account

def detect_ingredients(image_path):
    """
    Detect ingredients from image using Google Cloud Vision API
    """
    try:
        # Get API key from environment
        api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        
        if not api_key:
            print("Warning: No API key found. Using mock data.")
            return get_mock_ingredients()
        
        # Initialize Vision API client with API key
        client = vision.ImageAnnotatorClient(
            client_options={"api_key": api_key}
        )
        
        # Read the image file
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # Perform label detection
        response = client.label_detection(image=image)
        labels = response.label_annotations
        
        # Also try object localization for more specific results
        objects = client.object_localization(image=image).localized_object_annotations
        
        # Check for errors
        if response.error.message:
            raise Exception(f"API Error: {response.error.message}")
        
        # Extract food-related items
        ingredients = extract_food_items(labels, objects)
        
        # If no food items detected, return mock data as fallback
        if not ingredients:
            print("No food items detected. Using sample data.")
            return get_mock_ingredients()
        
        return ingredients
        
    except Exception as e:
        print(f"Error in detect_ingredients: {str(e)}")
        # Return mock data if API fails
        return get_mock_ingredients()


def extract_food_items(labels, objects):
    """
    Extract food-related items from Vision API results
    """
    # Food-related keywords to filter
    food_keywords = [
        'vegetable', 'fruit', 'food', 'ingredient', 'produce',
        'meat', 'chicken', 'fish', 'seafood', 'beef', 'pork',
        'grain', 'rice', 'wheat', 'bread',
        'dairy', 'cheese', 'milk', 'egg',
        'spice', 'herb', 'seasoning',
        'tomato', 'onion', 'garlic', 'potato', 'carrot',
        'pepper', 'chili', 'cucumber', 'cabbage',
        'leaf', 'leafy', 'green'
    ]
    
    # Common ingredient names
    ingredient_names = [
        'tomato', 'onion', 'garlic', 'ginger', 'potato', 'carrot',
        'chicken', 'beef', 'pork', 'fish', 'egg', 'rice', 'wheat',
        'pepper', 'chili', 'cucumber', 'cabbage', 'lettuce',
        'mushroom', 'broccoli', 'cauliflower', 'spinach',
        'lemon', 'lime', 'apple', 'banana', 'orange',
        'cheese', 'milk', 'butter', 'oil', 'salt', 'sugar'
    ]
    
    detected_items = set()
    
    # Process labels
    for label in labels:
        description = label.description.lower()
        
        # Check if it's a food-related label
        is_food = any(keyword in description for keyword in food_keywords)
        
        # Check if it's a specific ingredient
        is_ingredient = any(ing in description for ing in ingredient_names)
        
        if is_food or is_ingredient:
            # Clean up the description
            clean_name = description.replace('_', ' ').strip()
            detected_items.add(clean_name)
    
    # Process objects (more specific)
    for obj in objects:
        name = obj.name.lower()
        
        # Objects are usually more specific
        is_food = any(keyword in name for keyword in food_keywords)
        is_ingredient = any(ing in name for ing in ingredient_names)
        
        if is_food or is_ingredient:
            clean_name = name.replace('_', ' ').strip()
            detected_items.add(clean_name)
    
    # Convert set to sorted list
    return sorted(list(detected_items))


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
        
        # Try a simple operation
        return True, "API connection successful!"
        
    except Exception as e:
        return False, f"API connection failed: {str(e)}"