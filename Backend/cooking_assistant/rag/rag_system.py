"""
Main RAG System - orchestrates retrieval and generation
"""

import os
import json
from typing import List, Dict, Any
from .retrieval.retriever import RecipeRetriever
from .retrieval.semantic_search import SemanticRecipeSearch
from .vector_db.embeddings import EmbeddingManager
from .evaluation.metrics import RAGEvaluator
from .generation.response_generator import ResponseGenerator
from .memory.conversation_memory import ConversationMemory


class RAGSystem:
    """Main RAG orchestrator for cooking assistant"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

        print("\n" + "="*60)
        print("Initializing RAG System...")
        print("="*60)

        # Use the largest available database
        db_path = self._find_best_database(data_dir)
        print(f"Using database: {db_path}")

        self.retriever     = RecipeRetriever(db_path)
        self.semantic_search = SemanticRecipeSearch()
        self.embeddings    = EmbeddingManager(
            os.path.join(data_dir, 'embeddings')
        )
        self.evaluator = RAGEvaluator(data_dir)
        self.generator = ResponseGenerator()
        self.memory    = ConversationMemory()

        print("✓ RAG System initialized successfully\n")

    def _find_best_database(self, data_dir: str) -> str:
        """Find the largest recipe database available"""
        candidates = [
            os.path.join(data_dir, 'recipes_all_merged.json'),
            os.path.join(data_dir, 'new_200_recipes.json'),
            os.path.join(data_dir, 'recipes', 'recipe_database.json'),
            os.path.join(data_dir, 'recipe_database.json'),
        ]
        best_path  = candidates[-1]
        best_count = 0

        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    count = (
                        len(data)
                        if isinstance(data, list)
                        else len(data.get('recipes', []))
                    )
                    print(f"  Found: {os.path.basename(path)} ({count} recipes)")
                    if count > best_count:
                        best_count = count
                        best_path  = path
                except Exception:
                    pass

        print(f"  → Selected: {os.path.basename(best_path)} ({best_count} recipes)")
        return best_path

    def search_recipes(
        self,
        user_ingredients: List[str],
        top_k: int = 12,
        use_memory: bool = True,
    ) -> Dict[str, Any]:
        """
        Main search — finds recipes, filters via memory,
        then generates a natural language recommendation.
        """
        recipes = self.retriever.get_all_recipes()

        if not recipes:
            return {
                'success':        False,
                'error':          'No recipes in database',
                'results':        [],
                'recommendation': '',
            }

        # Track search in memory
        self.memory.remember_search(user_ingredients)

        # Semantic search
        results = self.semantic_search.search(user_ingredients, recipes, top_k)

        # Filter by memory (remove rejected, apply dietary prefs)
        if use_memory:
            results = self.memory.filter_results(results)

        # Generate natural language recommendation
        user_prefs           = self.memory.user_preferences or None
        conversation_history = self.memory.get_messages_for_api()

        recommendation = self.generator.generate_recommendation(
            user_ingredients     = user_ingredients,
            retrieved_recipes    = results[:5],
            user_preferences     = user_prefs,
            conversation_history = conversation_history if conversation_history else None,
        )

        # Save assistant response to memory
        self.memory.add_message('assistant', recommendation)

        return {
            'success':        True,
            'query':          user_ingredients,
            'results':        results,
            'total_found':    len(results),
            'database_size':  len(recipes),
            'recommendation': recommendation,
            'context':        self.memory.get_context_summary(),
        }

    def chat(
        self,
        user_message: str,
        user_ingredients: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Conversational interface — remembers past messages
        and responds naturally.
        """
        self.memory.add_message('user', user_message)

        if user_ingredients:
            return self.search_recipes(user_ingredients)

        # Pure conversation — no ingredient search
        history  = self.memory.get_messages_for_api()
        response = self.generator._call_claude(history)
        self.memory.add_message('assistant', response)

        return {
            'success':        True,
            'recommendation': response,
            'results':        [],
        }

    def like_recipe(self, recipe_id: str, recipe_name: str):
        """Tell memory the user liked this recipe"""
        self.memory.like_recipe(recipe_id, recipe_name)

    def reject_recipe(self, recipe_id: str, recipe_name: str, reason: str = ''):
        """Tell memory the user rejected this recipe"""
        self.memory.reject_recipe(recipe_id, recipe_name, reason)

    def set_preference(self, key: str, value: Any):
        """Store a user preference in memory"""
        self.memory.set_preference(key, value)

    def get_recipe_details(self, recipe_id: str) -> Dict[str, Any]:
        recipe = self.retriever.get_recipe_by_id(recipe_id)
        return recipe if recipe else {'error': 'Recipe not found'}

    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:
        return self.retriever.get_recipes_by_category(category)

    def filter_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        return self.retriever.get_recipes_by_difficulty(difficulty)

    def get_database_stats(self) -> Dict[str, Any]:
        return self.retriever.get_database_stats()

    def ingest_cookbooks(self, cookbooks_dir: str) -> Dict[str, Any]:
        """
        Parse cookbooks folder and add recipes to database.
        Call this once to populate recipe_database.json from PDFs/text files.
        """
        from .ingestion.cookbook_parser import CookbookParser

        output_path = os.path.join(self.data_dir, 'recipe_database.json')
        parser = CookbookParser(
            cookbooks_dir=cookbooks_dir,
            output_path=output_path,
        )

        recipes = parser.parse_all()
        parser.save_to_database(recipes)

        # Reload retriever after ingestion
        self.retriever = RecipeRetriever(output_path)

        return {
            'success':       True,
            'new_recipes':   len(recipes),
            'total_recipes': len(self.retriever.get_all_recipes()),
        }