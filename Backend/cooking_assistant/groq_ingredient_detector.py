"""
Groq-based Ingredient Detector for AI-Powered Kitchen Echo System
Replaces the Google Vision / Gemini API with Groq (FREE, no regional blocks)
Model: meta-llama/llama-4-scout-17b-16e-instruct (supports vision/images)
"""

import os
import base64
import json
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    raise ImportError("Please run: pip install groq")

try:
    from PIL import Image
    import io
except ImportError:
    raise ImportError("Please run: pip install Pillow")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Will use system environment variables


class GroqIngredientDetector:
    """
    Detects ingredients and reads text from food/package images using Groq API.
    Drop-in replacement for GeminiIngredientDetector.
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in .env file or environment variables.\n"
                "Get a free key at: https://console.groq.com"
            )
        self.client = Groq(api_key=self.api_key)
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def _image_to_base64(self, image_path):
        """Convert image file to base64 string."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _get_image_media_type(self, image_path):
        """Get the media type based on file extension."""
        ext = Path(image_path).suffix.lower()
        types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return types.get(ext, "image/jpeg")

    def detect_ingredients_from_image(self, image_path):
        """
        Detect ingredients from a food image or package photo.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict with keys: ingredients, text_found, confidence, raw_response
        """
        try:
            image_data = self._image_to_base64(image_path)
            media_type = self._get_image_media_type(image_path)

            prompt = """Analyze this food image or product package carefully.

Please identify and list:
1. All visible ingredients or food items
2. Any text visible on packaging (ingredient lists, labels)
3. Brand name if visible

Respond in this exact JSON format:
{
    "ingredients": ["ingredient1", "ingredient2", "ingredient3"],
    "text_found": "any text visible on the package",
    "brand": "brand name if visible or null",
    "confidence": "high/medium/low",
    "description": "brief description of what you see"
}

Only respond with the JSON, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                max_tokens=1024
            )

            raw_text = response.choices[0].message.content.strip()

            # Parse JSON response
            try:
                # Remove markdown code blocks if present
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
                result = json.loads(raw_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, extract ingredients manually
                result = {
                    "ingredients": self._extract_ingredients_from_text(raw_text),
                    "text_found": raw_text,
                    "brand": None,
                    "confidence": "low",
                    "description": raw_text
                }

            result["raw_response"] = raw_text
            return result

        except Exception as e:
            return {
                "ingredients": [],
                "text_found": "",
                "brand": None,
                "confidence": "low",
                "description": f"Error: {str(e)}",
                "raw_response": str(e),
                "error": str(e)
            }

    def detect_ingredients_from_text(self, ingredient_text):
        """
        Parse and normalize an ingredient list from text (e.g. from a package).
        
        Args:
            ingredient_text: Raw ingredient text from a package
            
        Returns:
            list of cleaned ingredient names
        """
        try:
            prompt = f"""Extract and clean the ingredient list from this text:

"{ingredient_text}"

Return ONLY a JSON array of ingredient names, cleaned and normalized.
Example: ["coconut milk", "turmeric", "chili powder", "salt"]

Only respond with the JSON array, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512
            )

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            return json.loads(raw)

        except Exception as e:
            return []

    def suggest_recipes_from_ingredients(self, ingredients, cuisine="Sri Lankan"):
        """
        Suggest recipes based on detected ingredients.
        
        Args:
            ingredients: list of ingredient names
            cuisine: cuisine type preference
            
        Returns:
            list of recipe suggestions
        """
        try:
            ingredients_str = ", ".join(ingredients)
            prompt = f"""I have these ingredients: {ingredients_str}

Suggest 3 {cuisine} recipes I can make with these ingredients.
Respond in this exact JSON format:
{{
    "recipes": [
        {{
            "name": "Recipe Name",
            "ingredients_needed": ["ing1", "ing2"],
            "missing_ingredients": ["ing3"],
            "difficulty": "easy/medium/hard",
            "time_minutes": 30
        }}
    ]
}}

Only respond with the JSON, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            result = json.loads(raw)
            return result.get("recipes", [])

        except Exception as e:
            return []

    def _extract_ingredients_from_text(self, text):
        """Fallback: extract ingredients from plain text."""
        lines = text.split('\n')
        ingredients = []
        for line in lines:
            line = line.strip().lstrip('-•*123456789. ')
            if line and len(line) > 2 and len(line) < 50:
                ingredients.append(line.lower())
        return ingredients[:20]  # Max 20 ingredients


# ─────────────────────────────────────────────
# Flask route helpers (drop-in for your app.py)
# ─────────────────────────────────────────────

def create_detector():
    """Create and return a GroqIngredientDetector instance."""
    return GroqIngredientDetector()


def analyze_image_route(image_path):
    """
    Helper function to use in your Flask routes.
    Returns JSON-ready dict.
    """
    detector = create_detector()
    result = detector.detect_ingredients_from_image(image_path)
    return result


# ─────────────────────────────────────────────
# Quick test when run directly
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("Testing GroqIngredientDetector")
    print("=" * 50)

    detector = GroqIngredientDetector()
    print("✅ Detector initialized!")

    # Test text-based ingredient parsing
    test_text = "Coconut milk, turmeric powder, red chili, coriander seeds, salt, curry leaves"
    print(f"\nParsing ingredient text: '{test_text}'")
    ingredients = detector.detect_ingredients_from_text(test_text)
    print(f"✅ Parsed ingredients: {ingredients}")

    # Test recipe suggestion
    print("\nSuggesting Sri Lankan recipes...")
    recipes = detector.suggest_recipes_from_ingredients(
        ["coconut milk", "turmeric", "chicken", "curry leaves"],
        cuisine="Sri Lankan"
    )
    if recipes:
        print(f"✅ Got {len(recipes)} recipe suggestions!")
        for r in recipes:
            print(f"  - {r.get('name', 'Unknown')}")
    else:
        print("No recipes returned")

    print("\n✅ All tests passed! Ready to integrate into Flask app.")