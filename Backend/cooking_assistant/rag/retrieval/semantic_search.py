import re
from typing import List, Dict, Any, Tuple


class SemanticRecipeSearch:

    KEY_INGREDIENTS = [
        'chicken', 'fish', 'prawn', 'crab', 'mutton', 'lamb', 'beef',
        'pork', 'egg', 'tuna', 'sardine', 'shrimp', 'lentil', 'dhal',
        'chickpea', 'kadala', 'bitter gourd', 'karawila', 'jackfruit',
        'coconut milk', 'coconut cream', 'string hopper', 'hopper',
        'pittu', 'rice flour', 'semolina',
    ]

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.sbert_available    = False
        self.model              = None
        self._recipe_embeddings = None
        self._recipes_count     = 0

        try:
            from sentence_transformers import SentenceTransformer, util
            self.model           = SentenceTransformer(model_name)
            self.util            = util
            self.sbert_available = True
            print("✓ SBERT model loaded")
        except Exception as e:
            print(f"⚠ SBERT not available: {e}")

    def _safe_str(self, value) -> str:
        if value is None:
            return ''
        if isinstance(value, dict):
            return value.get('english', '') or value.get('en', '') or ''
        return str(value)

    def _get_recipe_name(self, recipe: Dict) -> str:
        names = recipe.get('names', {})
        if isinstance(names, dict):
            name = names.get('english', '') or names.get('en', '')
        else:
            name = str(names) if names else ''
        return name or recipe.get('name', 'Unknown Recipe')

    def _is_bad_recipe(self, recipe: Dict) -> bool:
        name = self._get_recipe_name(recipe).lower().strip()
        bad_patterns = [
            'page 1', 'page 2', 'page 3', '---',
            'placeholder', 'test recipe',
            'instructions to be added', 'to be added',
        ]
        if any(p in name for p in bad_patterns):
            return True
        if len(name) < 3:
            return True
        instructions = str(recipe.get('instructions', '') or recipe.get('method', ''))
        if 'instructions to be added' in instructions.lower():
            return True
        if 'detailed cooking instructions' in instructions.lower():
            return True
        return False

    def _clean_ingredient(self, raw: str) -> str:
        s = str(raw).strip()

        # Remove leading quantities like "1 kg", "2 cloves", "1/2 cup"
        s = re.sub(
            r'^\d+[\d./]*\s*(g|kg|mg|ml|l|cup|cups|tsp|tbsp|oz|lb|piece|pieces|'
            r'can|tin|medium|large|small|bunch|handful|cloves?|clove|inch|cm|'
            r'slice|slices|stalk|stalks|sprig|sprigs|pinch|drop|drops|sheet|sheets)?\s*',
            '', s, flags=re.IGNORECASE
        )

        # Take only text BEFORE the first comma
        # "chicken, cut into pieces" → "chicken"
        if ',' in s:
            s = s.split(',')[0].strip()

        # Remove trailing prep notes
        s = re.sub(
            r'\s+(sliced|diced|chopped|minced|grated|crushed|cubed|cut|peeled|'
            r'washed|cooked|raw|fresh|dried|ground|whole|boneless|skinless|'
            r'boiled|fried|finely|roughly|thinly|thickly|cleaned|rinsed|'
            r'soaked|roasted|toasted|blended|mashed|shredded|julienned)\b.*$',
            '', s, flags=re.IGNORECASE
        )

        return s.strip().lower()

    def _extract_recipe_ingredients(self, recipe: Dict) -> List[str]:
        result = []
        for ing in recipe.get('ingredients', []):
            if isinstance(ing, dict):
                # Handle: {'name': '1 kg chicken, cut into pieces', 'amount': ''}
                ing_name = ing.get('name', '')
                if isinstance(ing_name, dict):
                    ing_name = ing_name.get('english', '') or ing_name.get('en', '')
            else:
                ing_name = str(ing)

            cleaned = self._clean_ingredient(self._safe_str(ing_name))
            if (cleaned
                    and 'ingredients to be added' not in cleaned
                    and len(cleaned) > 1):
                result.append(cleaned)
        return result

    def _build_recipe_text(self, recipe: Dict) -> str:
        name     = self._get_recipe_name(recipe)
        ings     = self._extract_recipe_ingredients(recipe)
        category = self._safe_str(recipe.get('category', ''))
        parts    = [name]
        if category:
            parts.append(f"Category: {category}")
        if ings:
            parts.append(f"Ingredients: {', '.join(ings[:15])}")
        return '. '.join(parts)

    def _matches(self, user_ing: str, recipe_ing: str) -> bool:
        u = user_ing.lower().strip()
        r = recipe_ing.lower().strip()
        if not u or not r:
            return False
        if u == r:
            return True
        if u in r or r in u:
            return True
        for word in u.split():
            if len(word) >= 3 and word in r:
                return True
        for word in r.split():
            if len(word) >= 3 and word in u:
                return True
        return False

    def _score_recipe(
        self,
        user_ingredients: List[str],
        recipe_ings: List[str],
        recipe_name: str,
    ) -> Tuple[float, List[str], List[str], int]:

        matched = []
        missing = []

        for ri in recipe_ings:
            if any(self._matches(ui, ri) for ui in user_ingredients):
                matched.append(ri)
            else:
                missing.append(ri)

        covered_count = len(matched)
        total_count   = len(recipe_ings)

        if covered_count == 0:
            return 0.0, [], recipe_ings, 0

        user_match_count = sum(
            1 for ui in user_ingredients
            if any(self._matches(ui, ri) for ri in recipe_ings)
        )

        recipe_coverage = covered_count / total_count
        user_coverage   = user_match_count / len(user_ingredients) if user_ingredients else 0
        name_lower      = recipe_name.lower()

        # Key ingredient bonus
        key_bonus = 0.0
        for ki in self.KEY_INGREDIENTS:
            user_has   = any(self._matches(ki, ui) for ui in user_ingredients)
            recipe_has = any(self._matches(ki, ri) for ri in recipe_ings)

            if user_has and recipe_has:
                key_bonus += 0.30
                if ki in name_lower:
                    key_bonus += 0.20

        key_bonus = min(key_bonus, 0.60)

        # 35% recipe coverage + 25% user coverage + 40% key ingredient
        score = (0.35 * recipe_coverage) + (0.25 * user_coverage) + (0.40 * key_bonus)
        score = min(100.0, round(score * 100, 2))

        return score, matched, missing, user_match_count

    def _precompute_embeddings(self, recipes: List[Dict]):
        if not self.sbert_available:
            return
        if (self._recipe_embeddings is not None
                and self._recipes_count == len(recipes)):
            return

        print(f"[SBERT] Generating embeddings for {len(recipes)} recipes...")
        texts = [self._build_recipe_text(r) for r in recipes]
        self._recipe_embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )
        self._recipes_count = len(recipes)
        print(f"✓ Embeddings done: {self._recipe_embeddings.shape}")

    def search(
        self,
        user_ingredients: List[str],
        recipes: List[Dict],
        top_k: int = 12,
    ) -> List[Dict]:

        if not user_ingredients or not recipes:
            return []

        # SBERT as secondary signal
        sbert_scores = {}
        if self.sbert_available:
            try:
                self._precompute_embeddings(recipes)
                user_text = f"Cooking with: {', '.join(user_ingredients)}"
                user_emb  = self.model.encode(
                    [user_text],
                    convert_to_tensor=True,
                    normalize_embeddings=True,
                )
                sims = self.util.cos_sim(user_emb, self._recipe_embeddings)
                sims = sims.squeeze(0).cpu().numpy()
                for idx, s in enumerate(sims):
                    sbert_scores[idx] = float(s)
            except Exception as e:
                print(f"[SBERT] Error: {e}")

        results = []

        for i, recipe in enumerate(recipes):

            if self._is_bad_recipe(recipe):
                continue

            recipe_ings = self._extract_recipe_ingredients(recipe)
            recipe_name = self._get_recipe_name(recipe)

            if not recipe_ings:
                continue

            primary_score, matched, missing, user_match_count = self._score_recipe(
                user_ingredients, recipe_ings, recipe_name
            )

            if user_match_count == 0:
                continue

            # Blend with SBERT (small weight for tie-breaking)
            if sbert_scores:
                sem_raw     = sbert_scores.get(i, 0.3)
                sem_pct     = max(0, min(100, round((sem_raw - 0.2) / 0.7 * 100)))
                final_score = int(0.85 * primary_score + 0.15 * sem_pct)
            else:
                final_score = int(primary_score)

            final_score = max(0, min(100, final_score))

            if final_score < 5:
                continue

            cook_mins = recipe.get('cook_time_mins', recipe.get('cook_time_minutes', 30))
            prep_mins = recipe.get('prep_time_mins', recipe.get('prep_time_minutes', 10))
            method    = recipe.get('method', '') or recipe.get('instructions', '')
            cat       = self._safe_str(recipe.get('category', 'General'))
            diff      = self._safe_str(recipe.get('difficulty', 'medium'))

            results.append({
                'id':                  str(recipe.get('id', '')),
                'name':                recipe_name,
                'match_score':         final_score,
                'user_match_count':    user_match_count,
                'category':            cat,
                'difficulty':          diff,
                'cooking_time':        f"{cook_mins + prep_mins} mins",
                'cook_time_mins':      cook_mins,
                'prep_time_mins':      prep_mins,
                'matched_ingredients': matched,
                'missing_ingredients': missing[:8],
                'ingredients_used':    matched,
                'ingredients':         recipe.get('ingredients', []),
                'instructions':        recipe.get('instructions', method),
                'method':              method,
                'servings':            recipe.get('servings', 4),
                'cuisine':             'Sri Lankan',
                'region':              self._safe_str(recipe.get('region', '')),
                'spice_level':         recipe.get('spice_level', 2),
                'tips':                recipe.get('tips', ''),
                'cultural_note':       recipe.get('cultural_note', ''),
                'description':         recipe.get('description', ''),
                'search_method':       'rag-sbert' if self.sbert_available else 'keyword',
            })

        results.sort(
            key=lambda x: (x['user_match_count'], x['match_score']),
            reverse=True
        )

        return results[:top_k]