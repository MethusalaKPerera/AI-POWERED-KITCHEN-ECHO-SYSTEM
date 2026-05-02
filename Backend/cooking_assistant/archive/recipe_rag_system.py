#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) System for Recipe Retrieval
Uses sentence transformers for embeddings and FAISS for vector search
Supports trilingual search (English, Sinhala, Tamil)
For AI-Powered Kitchen Echo System Research Component
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import pickle

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'sentence-transformers', 'faiss-cpu', '--break-system-packages'])
    from sentence_transformers import SentenceTransformer
    import faiss


class RecipeRAG:
    """RAG system for trilingual recipe retrieval"""
    
    def __init__(self, recipe_db_path: str, embedding_model: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialize RAG system
        
        Args:
            recipe_db_path: Path to recipe database JSON
            embedding_model: Sentence transformer model name
                           Use multilingual for Sinhala/Tamil support
        """
        
        print(f"\n{'='*70}")
        print("🤖 INITIALIZING RAG SYSTEM")
        print(f"{'='*70}\n")
        
        # Load recipe database
        print(f"📚 Loading recipes from: {recipe_db_path}")
        with open(recipe_db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.recipes = data['recipes']
        
        print(f"OK Loaded {len(self.recipes)} recipes")
        
        # Load embedding model
        print(f"\n🔧 Loading embedding model: {embedding_model}")
        self.model = SentenceTransformer(embedding_model)
        print(f"OK Model loaded (dimension: {self.model.get_sentence_embedding_dimension()})")
        
        # Initialize variables
        self.index = None
        self.recipe_texts = []
        self.recipe_metadata = []
        
        # Create embeddings and index
        self.build_index()
    
    def create_recipe_text_representation(self, recipe: Dict) -> str:
        """
        Create a rich text representation of recipe for embedding
        Includes all languages for better multilingual search
        """
        
        parts = []
        
        # Names in all languages
        parts.append(f"Recipe: {recipe['name']}")
        if recipe.get('name_sinhala'):
            parts.append(f"{recipe['name_sinhala']}")
        if recipe.get('name_tamil'):
            parts.append(f"{recipe['name_tamil']}")
        
        # Description
        if recipe.get('description'):
            parts.append(f"Description: {recipe['description']}")
        
        # Category and region
        parts.append(f"Category: {recipe['category']}")
        if recipe.get('region'):
            parts.append(f"Region: {recipe['region']}")
        
        # Ingredients
        parts.append("Ingredients: " + ", ".join(recipe['ingredients']))
        
        # Instructions (first 3 steps for context)
        if recipe['instructions']:
            instructions_preview = ". ".join(recipe['instructions'][:3])
            parts.append(f"Method: {instructions_preview}")
        
        # Tags
        if recipe.get('tags'):
            parts.append("Tags: " + ", ".join(recipe['tags']))
        
        # Difficulty and timing
        parts.append(f"Difficulty: {recipe['difficulty']}")
        parts.append(f"Time: {recipe['prep_time_minutes']} + {recipe['cook_time_minutes']} minutes")
        
        return " | ".join(parts)
    
    def build_index(self):
        """Build FAISS index from recipes"""
        
        print(f"\n🔨 Building vector index...")
        
        # Create text representations
        self.recipe_texts = []
        self.recipe_metadata = []
        
        for recipe in self.recipes:
            text = self.create_recipe_text_representation(recipe)
            self.recipe_texts.append(text)
            self.recipe_metadata.append({
                'id': recipe['id'],
                'name': recipe['name'],
                'name_sinhala': recipe.get('name_sinhala', ''),
                'name_tamil': recipe.get('name_tamil', ''),
                'category': recipe['category'],
                'full_recipe': recipe
            })
        
        print(f"NOTE Created {len(self.recipe_texts)} text representations")
        
        # Generate embeddings
        print("🧮 Generating embeddings...")
        embeddings = self.model.encode(
            self.recipe_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"OK Generated embeddings: {embeddings.shape}")
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        
        # Use IndexFlatL2 for exact search (good for small datasets)
        # For larger datasets, use IndexIVFFlat for faster approximate search
        self.index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        print(f"OK FAISS index built: {self.index.ntotal} vectors")
        print(f"{'='*70}\n")
    
    def search(self, query: str, k: int = 5, language: str = 'english') -> List[Dict]:
        """
        Search for recipes using semantic similarity
        
        Args:
            query: Search query (can be in English, Sinhala, or Tamil)
            k: Number of results to return
            language: Response language preference
        
        Returns:
            List of matching recipes with scores
        """
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Prepare results
        results = []
        
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0]), 1):
            if idx < len(self.recipe_metadata):
                metadata = self.recipe_metadata[idx]
                recipe = metadata['full_recipe']
                
                # Calculate similarity score (convert distance to similarity)
                # Lower distance = higher similarity
                similarity_score = 1 / (1 + distance)
                
                # Get recipe name in requested language
                if language == 'sinhala':
                    display_name = metadata['name_sinhala'] or metadata['name']
                elif language == 'tamil':
                    display_name = metadata['name_tamil'] or metadata['name']
                else:
                    display_name = metadata['name']
                
                result = {
                    'rank': i,
                    'recipe_id': metadata['id'],
                    'recipe_name': display_name,
                    'recipe_name_english': metadata['name'],
                    'category': metadata['category'],
                    'similarity_score': float(similarity_score),
                    'distance': float(distance),
                    'recipe': recipe
                }
                
                results.append(result)
        
        return results
    
    def save_model(self, save_dir: str):
        """Save the RAG model for later use"""
        
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(save_path / 'recipe_index.faiss'))
        
        # Save metadata
        with open(save_path / 'recipe_metadata.pkl', 'wb') as f:
            pickle.dump({
                'recipe_texts': self.recipe_texts,
                'recipe_metadata': self.recipe_metadata
            }, f)
        
        # Save config
        config = {
            'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',
            'num_recipes': len(self.recipes),
            'embedding_dimension': self.model.get_sentence_embedding_dimension()
        }
        
        with open(save_path / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"OK Model saved to: {save_path}")
    
    def load_model(self, load_dir: str):
        """Load a saved RAG model"""
        
        load_path = Path(load_dir)
        
        # Load FAISS index
        self.index = faiss.read_index(str(load_path / 'recipe_index.faiss'))
        
        # Load metadata
        with open(load_path / 'recipe_metadata.pkl', 'rb') as f:
            data = pickle.load(f)
            self.recipe_texts = data['recipe_texts']
            self.recipe_metadata = data['recipe_metadata']
        
        print(f"OK Model loaded from: {load_path}")


class RAGEvaluator:
    """Evaluate RAG system performance for research"""
    
    def __init__(self, rag_system: RecipeRAG):
        self.rag = rag_system
    
    def evaluate_search_quality(self, test_queries: List[Dict]) -> Dict:
        """
        Evaluate search quality with test queries
        
        Args:
            test_queries: List of dicts with 'query', 'expected_category', 'language'
        
        Returns:
            Evaluation metrics
        """
        
        print(f"\n{'='*70}")
        print("STATS EVALUATING RAG SYSTEM")
        print(f"{'='*70}\n")
        
        correct_category = 0
        total_queries = len(test_queries)
        
        category_accuracy = {}
        language_accuracy = {}
        
        for test in test_queries:
            query = test['query']
            expected_cat = test.get('expected_category')
            language = test.get('language', 'english')
            
            # Search
            results = self.rag.search(query, k=1, language=language)
            
            if results:
                top_result = results[0]
                actual_cat = top_result['category']
                
                # Check if category matches
                if expected_cat and actual_cat == expected_cat:
                    correct_category += 1
                    
                    # Track per-category accuracy
                    if expected_cat not in category_accuracy:
                        category_accuracy[expected_cat] = {'correct': 0, 'total': 0}
                    category_accuracy[expected_cat]['correct'] += 1
                
                # Track per-language
                if language not in language_accuracy:
                    language_accuracy[language] = {'correct': 0, 'total': 0}
                if expected_cat and actual_cat == expected_cat:
                    language_accuracy[language]['correct'] += 1
                language_accuracy[language]['total'] += 1
            
            if expected_cat:
                if expected_cat not in category_accuracy:
                    category_accuracy[expected_cat] = {'correct': 0, 'total': 0}
                category_accuracy[expected_cat]['total'] += 1
        
        # Calculate metrics
        overall_accuracy = correct_category / total_queries if total_queries > 0 else 0
        
        # Per-category accuracy
        cat_acc_pct = {}
        for cat, stats in category_accuracy.items():
            cat_acc_pct[cat] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        # Per-language accuracy
        lang_acc_pct = {}
        for lang, stats in language_accuracy.items():
            lang_acc_pct[lang] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        metrics = {
            'overall_accuracy': overall_accuracy * 100,
            'total_queries': total_queries,
            'correct_predictions': correct_category,
            'category_accuracy': cat_acc_pct,
            'language_accuracy': lang_acc_pct
        }
        
        # Print results
        print(f"Overall Accuracy: {metrics['overall_accuracy']:.1f}%")
        print(f"Correct: {correct_category}/{total_queries}")
        print(f"\nPer-Category Accuracy:")
        for cat, acc in cat_acc_pct.items():
            print(f"  {cat}: {acc:.1f}%")
        print(f"\nPer-Language Accuracy:")
        for lang, acc in lang_acc_pct.items():
            print(f"  {lang}: {acc:.1f}%")
        
        print(f"\n{'='*70}\n")
        
        return metrics


def demo_rag_system():
    """Demo the RAG system"""
    
    # Paths (relative to cooking_assistant folder)
    recipe_db = 'rag/data/recipes/recipe_database.json'
    save_dir = 'rag/data/embeddings'
    
    try:
        # Initialize RAG
        rag = RecipeRAG(recipe_db)
        
        # Save model
        print("\n Saving model...")
        rag.save_model(save_dir)
        
        # Demo searches
        print("\n" + "="*70)
        print(" DEMO SEARCHES")
        print("="*70 + "\n")
        
        test_queries = [
            ("spicy chicken dish", "english"),
            ("කුකුල් මස් කරිය", "sinhala"),  # Chicken curry in Sinhala
            ("தேங்காய் சம்பல்", "tamil"),  # Coconut sambol in Tamil
            ("vegetarian protein", "english"),
            ("quick easy recipe", "english")
        ]
        
        for query, language in test_queries:
            print(f"\nQuery: '{query}' (Language: {language})")
            print("-" * 70)
            
            results = rag.search(query, k=3, language=language)
            
            for result in results:
                print(f"{result['rank']}. {result['recipe_name']}")
                print(f"   Category: {result['category']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
        
        # Evaluation
        print("\n" + "="*70)
        print("STATS EVALUATION")
        print("="*70)
        
        evaluation_queries = [
            {'query': 'chicken curry', 'expected_category': 'Curry', 'language': 'english'},
            {'query': 'කුකුල් මස්', 'expected_category': 'Curry', 'language': 'sinhala'},
            {'query': 'பருப்பு', 'expected_category': 'Curry', 'language': 'tamil'},
            {'query': 'coconut sambol', 'expected_category': 'Sambol', 'language': 'english'},
            {'query': 'spicy condiment', 'expected_category': 'Sambol', 'language': 'english'}
        ]
        
        evaluator = RAGEvaluator(rag)
        metrics = evaluator.evaluate_search_quality(evaluation_queries)
        
        # Save metrics
        metrics_path = Path(save_dir) / 'evaluation_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"STATS Metrics saved to: {metrics_path}")
        
    except FileNotFoundError as e:
        print(f"\nERROR Error: {e}")
        print("\n💡 First run: integrated_recipe_collector.py")


if __name__ == "__main__":
    demo_rag_system()