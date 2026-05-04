import json
import os
from typing import List, Dict, Any

class RecipeRetriever:
    """Loads and retrieves recipes from database"""

    def __init__(self, recipe_db_path: str):
        self.recipe_db_path = recipe_db_path
        self.recipes = self._load_recipes()
        print(f"✓ Loaded {len(self.recipes)} recipes from database")

    def _safe_str(self, value) -> str:
        """Safely convert any value to string"""
        if value is None:
            return ''
        if isinstance(value, dict):
            return value.get('english', '') or value.get('en', '') or str(list(value.values())[0]) if value else ''
        return str(value)

    def _load_recipes(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.recipe_db_path):
            try:
                with open(self.recipe_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data.get('recipes', [])
                    return data
            except json.JSONDecodeError as e:
                print(f"Error loading recipes: {e}")
                return []
        else:
            print(f"⚠ Recipe database not found at {self.recipe_db_path}")
            return []

    def get_all_recipes(self) -> List[Dict[str, Any]]:
        return self.recipes

    def get_recipe_by_id(self, recipe_id: str) -> Dict[str, Any]:
        for recipe in self.recipes:
            if str(recipe.get('id', '')) == str(recipe_id):
                return recipe
        return {}

    def get_recipes_by_category(self, category: str) -> List[Dict[str, Any]]:
        results = []
        for r in self.recipes:
            cat = self._safe_str(r.get('category', ''))
            if cat.lower() == category.lower():
                results.append(r)
        return results

    def get_recipes_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        results = []
        for r in self.recipes:
            diff = self._safe_str(r.get('difficulty', ''))
            if diff.lower() == difficulty.lower():
                results.append(r)
        return results

    def search_by_name(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        results = []
        for recipe in self.recipes:
            name = self._safe_str(recipe.get('name', '')).lower()
            names = recipe.get('names', {})
            if isinstance(names, dict):
                english_name = self._safe_str(names.get('english', '')).lower()
                if query_lower in english_name or query_lower in name:
                    results.append(recipe)
            elif query_lower in name:
                results.append(recipe)
        return results

    def get_database_stats(self) -> Dict[str, Any]:
        categories = {}
        difficulties = {}

        for recipe in self.recipes:
            # Safely extract category — handles str, dict, or None
            cat_raw  = recipe.get('category', 'Unknown')
            diff_raw = recipe.get('difficulty', 'medium')

            cat  = self._safe_str(cat_raw)  or 'Unknown'
            diff = self._safe_str(diff_raw) or 'medium'

            categories[cat]   = categories.get(cat, 0) + 1
            difficulties[diff] = difficulties.get(diff, 0) + 1

        return {
            'total_recipes': len(self.recipes),
            'categories':    categories,
            'difficulties':  difficulties,
        }