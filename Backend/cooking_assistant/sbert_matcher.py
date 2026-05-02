"""
STEP 3 — SBERT RECIPE MATCHER
================================
This file REPLACES the keyword matching in routes.py with
Sentence-BERT semantic matching.

Place this file in:
  Backend/cooking_assistant/sbert_matcher.py

Then update routes.py as shown at the bottom of this file.

How it works:
1. Loads the fine-tuned classifier from sbert_model_checkpoint.pth
2. When user sends ingredients, converts them to a 384-dim SBERT vector
3. Compares that vector against all recipe vectors using cosine similarity
4. Also uses the classifier to predict recipe category
5. Returns ranked recipes sorted by semantic similarity
"""

import os
import json
import re
import numpy as np
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer, util

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CKPT_FILE = os.path.join(BASE_DIR, 'sbert_model_checkpoint.pth')

# ── Category names ─────────────────────────────────────────────────────────────
CATEGORY_NAMES = {
    0: 'Curry',
    1: 'Rice',
    2: 'Breakfast',
    3: 'Snack',
    4: 'Festival',
    5: 'Dessert',
    6: 'Beverage',
}

# Main proteins — used for boosting relevant recipes
MAIN_PROTEINS = [
    'chicken', 'fish', 'prawn', 'crab', 'mutton', 'lamb', 'beef',
    'pork', 'egg', 'tuna', 'sardine', 'shrimp', 'lentil', 'dhal', 'parippu',
]


# ══════════════════════════════════════════════════════════════════════════════
# CLASSIFIER HEAD — same architecture as training
# ══════════════════════════════════════════════════════════════════════════════

class RecipeClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1     = nn.Linear(384, 128)
        self.relu    = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2     = nn.Linear(128, 7)

    def forward(self, x):
        return self.fc2(self.dropout(self.relu(self.fc1(x))))


# ══════════════════════════════════════════════════════════════════════════════
# SBERT MATCHER CLASS
# ══════════════════════════════════════════════════════════════════════════════

class SBERTRecipeMatcher:
    """
    Loads Sentence-BERT + fine-tuned classifier once.
    Provides semantic recipe search for the cooking assistant.
    """

    def __init__(self):
        self._sbert      = None
        self._classifier = None
        self._recipe_embeddings = None   # precomputed embeddings for all recipes
        self._recipes    = None          # list of recipe dicts
        self._loaded     = False

    def _load_models(self):
        """Lazy load — only loads when first recipe search is made."""
        if self._loaded:
            return

        print("[SBERT] Loading Sentence-BERT model...")
        self._sbert = SentenceTransformer('all-MiniLM-L6-v2')

        # Load fine-tuned classifier if checkpoint exists
        self._classifier = RecipeClassifier()
        if os.path.exists(CKPT_FILE):
            self._classifier.load_state_dict(
                torch.load(CKPT_FILE, map_location='cpu')
            )
            print(f"[SBERT] Loaded fine-tuned weights from {CKPT_FILE}")
        else:
            print(f"[SBERT] WARNING: No checkpoint found at {CKPT_FILE}")
            print(f"[SBERT] Run step2_train_sbert.py first!")
        self._classifier.eval()

        self._loaded = True
        print("[SBERT] Ready.")

    def _get_recipe_name(self, recipe):
        """Extract English recipe name."""
        names = recipe.get('names', {})
        if isinstance(names, dict):
            name = names.get('english', '') or names.get('en', '')
        else:
            name = str(names) if names else ''
        return name or recipe.get('name', 'Unknown Recipe')

    def _build_recipe_text(self, recipe):
        """Convert recipe dict to text for embedding."""
        name = self._get_recipe_name(recipe)
        
        ing_list = []
        for ing in recipe.get('ingredients', []):
            if isinstance(ing, dict):
                ing_name = ing.get('name', '')
                if isinstance(ing_name, dict):
                    ing_name = ing_name.get('english', '')
            else:
                ing_name = str(ing)
            # Strip numeric prefix
            ing_name = re.sub(
                r'^\d+[\d./]*\s*(g|kg|ml|l|cup|tsp|tbsp|oz|lb|piece|pieces)?\s*',
                '', ing_name.strip(), flags=re.IGNORECASE
            )
            if ing_name.strip():
                ing_list.append(ing_name.strip().lower())

        cat = recipe.get('category', '')
        parts = [name]
        if cat:
            parts.append(f"Category: {cat}")
        if ing_list:
            parts.append(f"Ingredients: {', '.join(ing_list)}")
        return '. '.join(parts)

    def _build_user_text(self, ingredients):
        """Convert user ingredient list to query text for embedding."""
        clean = [i.lower().strip() for i in ingredients if i.strip()]
        return f"Available ingredients: {', '.join(clean)}"

    def _precompute_recipe_embeddings(self, recipes):
        """Generate embeddings for all recipes — cached after first call."""
        if self._recipe_embeddings is not None and self._recipes == recipes:
            return

        print(f"[SBERT] Generating embeddings for {len(recipes)} recipes...")
        texts = [self._build_recipe_text(r) for r in recipes]
        
        # Encode in batches
        self._recipe_embeddings = self._sbert.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_tensor=True,
            normalize_embeddings=True,  # for cosine similarity
        )
        self._recipes = recipes
        print(f"[SBERT] Embeddings ready: {self._recipe_embeddings.shape}")

    def predict_category(self, text):
        """Predict recipe category using fine-tuned classifier."""
        self._load_models()
        embedding = self._sbert.encode([text], convert_to_numpy=True)
        tensor    = torch.FloatTensor(embedding)
        with torch.no_grad():
            output = self._classifier(tensor)
            probs  = torch.softmax(output, dim=1).squeeze()
            pred   = probs.argmax().item()
            conf   = probs[pred].item()
        return CATEGORY_NAMES.get(pred, 'Curry'), round(conf * 100, 1)

    def _keyword_fallback(self, user_ingredients, recipe_ings):
        """
        Fallback: keyword containment check.
        Used to count matched/missing ingredients for display purposes.
        Sentence-BERT handles the ranking — this is just for display.
        """
        matched = []
        missing = []
        for ri in recipe_ings:
            found = False
            for ui in user_ingredients:
                u = ui.lower().strip()
                r = ri.lower().strip()
                if u in r or r in u:
                    found = True
                    break
                # word-level
                for word in u.split():
                    if len(word) >= 3 and word in r:
                        found = True
                        break
                if found:
                    break
            if found:
                matched.append(ri)
            else:
                missing.append(ri)
        return matched, missing

    def search_recipes(self, user_ingredients, recipes, top_k=12):
        """
        Main semantic search function.
        
        Args:
            user_ingredients: list of ingredient strings from user
            recipes:          list of recipe dicts from your JSON
            top_k:            number of results to return
            
        Returns:
            list of recipe dicts with match_score, category etc.
        """
        self._load_models()
        self._precompute_recipe_embeddings(recipes)

        if not user_ingredients:
            return []

        # ── Encode user query ──────────────────────────────────────────────
        user_text = self._build_user_text(user_ingredients)
        user_embedding = self._sbert.encode(
            [user_text],
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        # ── Cosine similarity against all recipes ─────────────────────────
        # Shape: [1, n_recipes] → squeeze to [n_recipes]
        similarities = util.cos_sim(user_embedding, self._recipe_embeddings)
        similarities = similarities.squeeze(0).cpu().numpy()

        # ── Build results ──────────────────────────────────────────────────
        results = []
        for i, recipe in enumerate(recipes):
            sim_score = float(similarities[i])

            # Convert cosine similarity (0-1) to percentage (0-100)
            # Cosine similarity range for food text is roughly 0.3–0.9
            # Normalise to 0-100% range
            match_score = max(0, min(100, round((sim_score - 0.3) / 0.6 * 100)))

            # Only include if reasonably relevant
            if match_score < 10:
                continue

            # Get recipe name
            en_name = self._get_recipe_name(recipe)
            name_lower = en_name.lower()

            # Predict category using fine-tuned classifier
            recipe_text = self._build_recipe_text(recipe)
            predicted_cat, cat_confidence = self.predict_category(recipe_text)

            # Get clean ingredient list for display
            recipe_ings = []
            has_placeholder = False
            for ing in recipe.get('ingredients', []):
                if isinstance(ing, dict):
                    ing_name = ing.get('name', '')
                    if isinstance(ing_name, dict):
                        ing_name = ing_name.get('english', '')
                else:
                    ing_name = str(ing)
                    
                if "ingredients to be added" in ing_name.lower():
                    has_placeholder = True
                    break
                    
                ing_clean = re.sub(
                    r'^\d+[\d./]*\s*(g|kg|ml|l|cup|tsp|tbsp|oz|lb|piece|pieces)?\s*',
                    '', ing_name.strip(), flags=re.IGNORECASE
                ).strip().lower()
                if ing_clean:
                    recipe_ings.append(ing_clean)

            # Check instructions for placeholders
            method = recipe.get('method', '') or recipe.get('instructions', '')
            if not method or "instructions to be added" in method.lower() or "detailed cooking instructions" in method.lower():
                has_placeholder = True

            # Skip incomplete recipes
            if has_placeholder or not recipe_ings:
                continue

            matched_display, missing_ings = self._keyword_fallback(
                user_ingredients, recipe_ings
            )

            # Calculate actual ingredient overlap score
            covered_count = len(matched_display)
            total_count = len(recipe_ings)
            ing_score = round((covered_count / total_count) * 100) if total_count > 0 else 0

            # Blend semantic similarity with ingredient overlap to prevent 100% scores for mismatched ingredients
            # If ingredient overlap is 0, we cap the score to avoid misleading 100% matches
            if covered_count == 0:
                match_score = min(match_score, 40)
            else:
                match_score = int(0.4 * match_score + 0.6 * ing_score)

            # Main protein boost
            # If user has "chicken" and recipe is "Chicken Curry" → boost
            has_protein_match = any(
                p in name_lower and any(
                    p in ui.lower() for ui in user_ingredients
                )
                for p in MAIN_PROTEINS
            )
            if has_protein_match:
                match_score = min(100, match_score + 15)

            cook_mins = recipe.get('cook_time_mins',
                         recipe.get('cook_time_minutes', 30))
            prep_mins = recipe.get('prep_time_mins',
                         recipe.get('prep_time_minutes', 10))
            method    = recipe.get('method', '') or recipe.get('instructions', '')

            results.append({
                # Core matching
                'id':                    recipe.get('id', ''),
                'name':                  en_name,
                'match_score':           match_score,
                'semantic_similarity':   round(sim_score, 4),
                'predicted_category':    predicted_cat,
                'category_confidence':   cat_confidence,

                # Ingredients
                'matched_ingredients':   matched_display,
                'missing_ingredients':   missing_ings[:8],
                'ingredients_used':      matched_display,
                'ingredients':           recipe.get('ingredients', []),

                # Metadata
                'cuisine':               'Sri Lankan',
                'category':              recipe.get('category', predicted_cat),
                'region':                recipe.get('region', ''),
                'difficulty':            recipe.get('difficulty', 'medium'),
                'cooking_time':          f"{cook_mins + prep_mins} mins",
                'cook_time_mins':        cook_mins,
                'prep_time_mins':        prep_mins,
                'servings':              recipe.get('servings', 4),
                'spice_level':           recipe.get('spice_level', 2),
                'is_authentic':          recipe.get('is_authentic', True),
                'instructions':          recipe.get('instructions', method),
                'method':                method,
                'tips':                  recipe.get('tips', ''),
                'cultural_note':         recipe.get('cultural_note', ''),
                'description':           recipe.get('description', ''),
            })

        # ── Sort: protein match first, then semantic score ─────────────────
        results.sort(
            key=lambda x: (
                any(
                    p in x['name'].lower() and any(
                        p in ui.lower() for ui in user_ingredients
                    )
                    for p in MAIN_PROTEINS
                ),
                x['match_score'],
            ),
            reverse=True,
        )

        return results[:top_k]


# ── Singleton instance ─────────────────────────────────────────────────────────
_matcher = SBERTRecipeMatcher()


def sbert_search_recipes(user_ingredients, recipes, top_k=12):
    """
    Public function — call this from routes.py.
    
    Usage in routes.py:
        from sbert_matcher import sbert_search_recipes
        results = sbert_search_recipes(user_ingredients, recipes)
    """
    return _matcher.search_recipes(user_ingredients, recipes, top_k)


def sbert_predict_category(recipe_text):
    """
    Predict category of a recipe text.
    
    Usage:
        category, confidence = sbert_predict_category("Chicken Curry. Ingredients: ...")
    """
    return _matcher.predict_category(recipe_text)


# ══════════════════════════════════════════════════════════════════════════════
#
#  HOW TO UPDATE YOUR routes.py
#  ─────────────────────────────
#  Find the search_recipes function in routes.py and change it to:
#
#
#  @cooking_bp.route('/search-recipes', methods=['POST'])
#  def search_recipes():
#      data = request.get_json()
#      if not data or 'ingredients' not in data:
#          return jsonify({'error': 'No ingredients provided'}), 400
#
#      user_ingredients = [i.lower().strip() for i in data['ingredients']]
#      recipes          = _load_recipes()
#
#      # ── SBERT semantic search replaces keyword matching ──
#      from sbert_matcher import sbert_search_recipes
#      results = sbert_search_recipes(user_ingredients, recipes, top_k=12)
#
#      return jsonify({
#          'success':       True,
#          'recipes':       results,
#          'total_found':   len(results),
#          'database_size': len(recipes),
#      })
#
# ══════════════════════════════════════════════════════════════════════════════


if __name__ == '__main__':
    # Quick test
    print("Testing SBERT Matcher...")
    print("(Loads model — may take 30s on first run)\n")

    test_ingredients = ['chicken', 'onion', 'garlic', 'tomato', 'coconut milk']
    print(f"Test ingredients: {test_ingredients}")

    # Simple test without recipe database
    matcher = SBERTRecipeMatcher()
    matcher._load_models()

    # Test category prediction
    test_text = "Chicken Curry. Ingredients: chicken pieces, onion, tomato, coconut milk, curry powder"
    cat, conf = matcher.predict_category(test_text)
    print(f"\nCategory prediction for '{test_text[:40]}...'")
    print(f"  → {cat} ({conf}% confidence)")

    print("\n[✓] SBERT matcher working correctly!")
    print("[✓] Update routes.py as shown in the comments above.")
