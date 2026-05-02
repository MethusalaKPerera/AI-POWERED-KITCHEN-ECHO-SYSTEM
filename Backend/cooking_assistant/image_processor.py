"""
image_processor.py - Drop-in replacement using Groq Vision API
Replaces broken Google Vision with Groq's llama-4-scout vision model
"""

import os
import base64
import json
import re
from groq import Groq

# ── Groq client ──────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or "dummy_key"


client = Groq(api_key=GROQ_API_KEY)
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# ── helpers ───────────────────────────────────────────────────────────────────
def _encode_image(image_path: str) -> tuple[str, str]:
    """Return (base64_data, media_type)."""
    ext = os.path.splitext(image_path)[1].lower()
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8"), mime


def _parse_json_list(text: str) -> list[str]:
    """Extract a JSON array from model output, return [] on failure."""
    # Try direct parse
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(i).strip().lower() for i in data if str(i).strip()]
    except json.JSONDecodeError:
        pass

    # Try extracting [...] block
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return [str(i).strip().lower() for i in data if str(i).strip()]
        except json.JSONDecodeError:
            pass

    # Fall back: split lines/commas
    items = re.split(r"[\n,]+", text)
    cleaned = []
    for item in items:
        item = re.sub(r"^[\d\.\-\*\[\]\"\'\s]+", "", item).strip().strip('"\'')
        if 2 < len(item) < 50:
            cleaned.append(item.lower())
    return cleaned


# ── Public API ────────────────────────────────────────────────────────────────
def analyze_image(image_path: str) -> dict:
    """
    Analyse an image and return detected ingredients.

    Returns:
        {
            "success": bool,
            "ingredients": [...],
            "raw_text": str,
            "error": str | None
        }
    """
    try:
        b64, mime = _encode_image(image_path)

        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{b64}"
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "You are a food ingredient detection AI. "
                                "Look at this image carefully and list EVERY food ingredient "
                                "or raw food item you can see.\n\n"
                                "Rules:\n"
                                "- Look very carefully at the actual image\n"
                                "- List only what you genuinely see in this specific image\n"
                                "- Include vegetables, meats, spices, fruits, grains, etc.\n"
                                "- Use simple common names (e.g. 'onion', 'chicken', 'garlic')\n"
                                "- Return ONLY a JSON array of strings, nothing else\n\n"
                                "Example output: [\"chicken\", \"onion\", \"garlic\", \"tomato\", \"ginger\"]\n\n"
                                "Return ONLY the JSON array:"
                            ),
                        },
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.1,
        )

        raw = response.choices[0].message.content or ""
        ingredients = _parse_json_list(raw)

        if not ingredients:
            return {
                "success": False,
                "ingredients": [],
                "raw_text": raw,
                "error": "Could not detect any ingredients in the image.",
            }

        return {
            "success": True,
            "ingredients": ingredients,
            "raw_text": raw,
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "ingredients": [],
            "raw_text": "",
            "error": f"Groq API error: {str(exc)}",
        }


def detect_ingredients(image_path: str) -> list[str]:
    """Simple wrapper — returns ingredient list (empty on failure)."""
    result = analyze_image(image_path)
    return result.get("ingredients", [])


def process_image_for_recipes(image_path: str) -> dict:
    """
    Legacy-compatible wrapper used by some route handlers.

    Returns:
        {
            "success": bool,
            "ingredients": [...],
            "description": str,
            "error": str | None
        }
    """
    result = analyze_image(image_path)
    return {
        "success": result["success"],
        "ingredients": result["ingredients"],
        "description": f"Detected {len(result['ingredients'])} ingredients using Groq Vision AI.",
        "error": result.get("error"),
    }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        print(json.dumps(analyze_image(path), indent=2))
    else:
        # Connectivity test
        r = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5,
        )
        print("Groq connection OK:", r.choices[0].message.content)