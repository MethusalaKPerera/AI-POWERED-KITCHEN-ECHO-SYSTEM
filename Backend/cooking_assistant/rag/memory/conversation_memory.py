from typing import List, Dict, Any
from datetime import datetime

class ConversationMemory:
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.history = []
        self.user_preferences = {}
        self.past_searches = []
        self.rejected_recipes = []
        self.liked_recipes = []

    def _safe_id(self, recipe) -> str:
        """Always return a string ID safely"""
        if isinstance(recipe, dict):
            rid = recipe.get('id', '')
            if isinstance(rid, dict):
                return str(rid.get('english', '')) or str(rid)
            return str(rid)
        return str(recipe)

    def add_message(self, role: str, content: str):
        self.history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
        })
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def remember_search(self, ingredients: List[str]):
        self.past_searches.append({
            'ingredients': ingredients,
            'timestamp': datetime.now().isoformat(),
        })

    def like_recipe(self, recipe_id: str, recipe_name: str):
        safe_id = str(recipe_id)
        existing = [r for r in self.liked_recipes if self._safe_id(r) == safe_id]
        if not existing:
            self.liked_recipes.append({
                'id': safe_id,
                'name': recipe_name,
                'timestamp': datetime.now().isoformat(),
            })

    def reject_recipe(self, recipe_id: str, recipe_name: str, reason: str = ''):
        safe_id = str(recipe_id)
        existing = [r for r in self.rejected_recipes if self._safe_id(r) == safe_id]
        if not existing:
            self.rejected_recipes.append({
                'id': safe_id,
                'name': recipe_name,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
            })

    def set_preference(self, key: str, value: Any):
        self.user_preferences[key] = value
        print(f"✓ Preference saved: {key} = {value}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.user_preferences.get(key, default)

    def filter_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out rejected recipes and apply preferences"""

        # Build rejected ID set safely
        rejected_ids = set()
        for r in self.rejected_recipes:
            rejected_ids.add(self._safe_id(r))

        # Filter rejected
        filtered = [
            r for r in results
            if self._safe_id(r) not in rejected_ids
        ]

        # Filter by max cooking time
        max_time = self.get_preference('max_cook_time')
        if max_time:
            def within_time(recipe):
                time_str = recipe.get('cooking_time', '40 mins')
                try:
                    mins = int(str(time_str).replace(' mins', '').strip())
                    return mins <= int(max_time)
                except Exception:
                    return True
            filtered = [r for r in filtered if within_time(r)]

        # Filter vegetarian
        dietary = self.get_preference('dietary')
        if dietary == 'vegetarian':
            meat_keywords = [
                'chicken', 'beef', 'pork', 'fish', 'prawn',
                'mutton', 'lamb', 'tuna', 'sardine', 'shrimp'
            ]
            filtered = [
                r for r in filtered
                if not any(m in r.get('name', '').lower() for m in meat_keywords)
            ]

        return filtered

    def get_context_summary(self) -> str:
        parts = []
        if self.user_preferences:
            parts.append(f"User preferences: {self.user_preferences}")
        if self.liked_recipes:
            names = [r['name'] for r in self.liked_recipes[-3:]]
            parts.append(f"Recipes they liked before: {', '.join(names)}")
        if self.rejected_recipes:
            names = [r['name'] for r in self.rejected_recipes[-3:]]
            parts.append(f"Recipes they did not want: {', '.join(names)}")
        if self.past_searches:
            last = self.past_searches[-1]['ingredients']
            parts.append(f"Last search ingredients: {', '.join(last)}")
        return '\n'.join(parts) if parts else ''

    def get_messages_for_api(self) -> List[Dict[str, str]]:
        return [
            {'role': msg['role'], 'content': msg['content']}
            for msg in self.history[-10:]
        ]

    def clear(self):
        self.history = []
        self.user_preferences = {}
        self.past_searches = []
        self.rejected_recipes = []
        self.liked_recipes = []
        print("✓ Memory cleared")