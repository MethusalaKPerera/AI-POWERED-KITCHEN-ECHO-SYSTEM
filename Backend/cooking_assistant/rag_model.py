"""
Advanced RAG Model for Sri Lankan Recipe Search
Uses Sentence Transformers for semantic search (no ChromaDB needed)
"""

import os
from sentence_transformers import SentenceTransformer, util

class SriLankanRecipeRAG:
    def __init__(self):
        """Initialize the RAG model with sentence transformers"""
        print("🔧 Initializing Advanced RAG Model with Sentence Transformers...")
        
        # Load pre-trained model for embeddings
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Loaded sentence transformer model")
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            self.model = None
        
        self.recipes = []
        self.recipe_embeddings = []
        
    def load_recipes_from_folder(self, folder_path="data/sri_lankan_recipes"):
        """Load recipe text files and create embeddings"""
        print(f"📂 Loading recipes from: {folder_path}")
        
        if not os.path.exists(folder_path):
            print(f"⚠️ Folder not found: {folder_path}")
            return False
        
        recipe_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        
        if not recipe_files:
            print("⚠️ No recipe files found!")
            return False
        
        recipe_texts = []
        
        for idx, filename in enumerate(recipe_files):
            filepath = os.path.join(folder_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract recipe name from filename
                recipe_name = filename.replace('.txt', '').replace('_', ' ').title()
                
                # Parse ingredients and instructions
                ingredients = self._extract_ingredients(content)
                instructions = self._extract_instructions(content)
                
                # Store recipe data
                recipe_data = {
                    'id': idx + 1,
                    'name': recipe_name,
                    'filename': filename,
                    'content': content,
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'cuisine': 'Sri Lankan',
                    'source': 'RAG Model'
                }
                
                self.recipes.append(recipe_data)
                
                # Prepare text for embedding (combine name + ingredients for better matching)
                embedding_text = f"{recipe_name}. Ingredients: {', '.join(ingredients)}"
                recipe_texts.append(embedding_text)
                
                print(f"✅ Loaded: {recipe_name}")
                
            except Exception as e:
                print(f"❌ Error loading {filename}: {str(e)}")
        
        # Create embeddings if model is available
        if self.model and recipe_texts:
            try:
                print("🧠 Creating embeddings for semantic search...")
                self.recipe_embeddings = self.model.encode(recipe_texts, convert_to_tensor=True)
                print(f"✅ Created embeddings for {len(recipe_texts)} recipes")
            except Exception as e:
                print(f"⚠️ Error creating embeddings: {e}")
        
        print(f"\n🎉 Successfully loaded {len(self.recipes)} recipes!")
        return True
    
    def _extract_ingredients(self, content):
        """Extract ingredients list from recipe text"""
        ingredients = []
        lines = content.split('\n')
        
        in_ingredients = False
        for line in lines:
            line = line.strip()
            
            if 'Ingredients:' in line or 'ingredients:' in line.lower():
                in_ingredients = True
                continue
            
            if 'Instructions:' in line or 'instructions:' in line.lower():
                in_ingredients = False
                break
            
            if in_ingredients and line.startswith('-'):
                ingredient = line.lstrip('- ').strip()
                if ingredient:
                    ingredients.append(ingredient)
        
        return ingredients
    
    def _extract_instructions(self, content):
        """Extract cooking instructions from recipe text"""
        lines = content.split('\n')
        
        in_instructions = False
        instructions = []
        
        for line in lines:
            line = line.strip()
            
            if 'Instructions:' in line or 'instructions:' in line.lower():
                in_instructions = True
                continue
            
            if in_instructions and line:
                instructions.append(line)
        
        return ' '.join(instructions)
    
    def search_by_ingredients(self, ingredients, n_results=5):
        """
        Search for recipes based on available ingredients
        Uses semantic search with sentence transformers
        
        Args:
            ingredients: List of ingredient names
            n_results: Number of results to return
        
        Returns:
            List of matching recipes with scores
        """
        if not ingredients or not self.recipes:
            return []
        
        # Convert ingredients to lowercase for matching
        search_ingredients = [ing.lower().strip() for ing in ingredients]
        
        # Create search query
        query = f"Recipe with {', '.join(search_ingredients)}"
        
        scored_recipes = []
        
        # Use semantic search if embeddings are available
        if self.model and len(self.recipe_embeddings) > 0:
            try:
                # Encode the search query
                query_embedding = self.model.encode(query, convert_to_tensor=True)
                
                # Calculate cosine similarity
                similarities = util.cos_sim(query_embedding, self.recipe_embeddings)[0]
                
                # Get indices sorted by similarity
                top_results = similarities.argsort(descending=True)[:n_results]
                
                for idx in top_results:
                    recipe = self.recipes[int(idx)]
                    similarity_score = float(similarities[idx])
                    
                    # Calculate ingredient match score
                    match_score = self._calculate_match_score(
                        search_ingredients, 
                        recipe['ingredients']
                    )
                    
                    # Get matched and missing ingredients
                    matched = self._get_matched_ingredients(
                        search_ingredients,
                        recipe['ingredients']
                    )
                    
                    missing = self._get_missing_ingredients(
                        search_ingredients,
                        recipe['ingredients']
                    )
                    
                    # Combine semantic similarity and ingredient match
                    combined_score = int((similarity_score * 50) + (match_score * 0.5))
                    
                    scored_recipes.append({
                        'id': recipe['id'],
                        'name': recipe['name'],
                        'match_score': combined_score,
                        'semantic_score': int(similarity_score * 100),
                        'ingredient_match': match_score,
                        'cuisine': recipe['cuisine'],
                        'source': recipe['source'] + ' (Semantic Search)',
                        'ingredients': recipe['ingredients'],
                        'instructions': recipe['instructions'],
                        'matched_ingredients': matched,
                        'missing_ingredients': missing,
                        'cooking_time': self._estimate_cooking_time(recipe['name']),
                        'difficulty': self._estimate_difficulty(recipe['name']),
                        'servings': 4
                    })
                
            except Exception as e:
                print(f"⚠️ Semantic search error: {e}. Falling back to text matching.")
                # Fall back to simple text matching
                return self._simple_text_search(search_ingredients, n_results)
        
        else:
            # Fallback to simple text matching
            return self._simple_text_search(search_ingredients, n_results)
        
        # Sort by combined score
        scored_recipes.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_recipes
    
    def _simple_text_search(self, search_ingredients, n_results=5):
        """Fallback simple text matching"""
        scored_recipes = []
        
        for recipe in self.recipes:
            match_score = self._calculate_match_score(
                search_ingredients, 
                recipe['ingredients']
            )
            
            matched = self._get_matched_ingredients(
                search_ingredients,
                recipe['ingredients']
            )
            
            missing = self._get_missing_ingredients(
                search_ingredients,
                recipe['ingredients']
            )
            
            scored_recipes.append({
                'id': recipe['id'],
                'name': recipe['name'],
                'match_score': match_score,
                'cuisine': recipe['cuisine'],
                'source': recipe['source'],
                'ingredients': recipe['ingredients'],
                'instructions': recipe['instructions'],
                'matched_ingredients': matched,
                'missing_ingredients': missing,
                'cooking_time': self._estimate_cooking_time(recipe['name']),
                'difficulty': self._estimate_difficulty(recipe['name']),
                'servings': 4
            })
        
        scored_recipes.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_recipes[:n_results]
    
    def _calculate_match_score(self, search_ingredients, recipe_ingredients):
        """Calculate percentage match between search and recipe ingredients"""
        if not recipe_ingredients:
            return 0
        
        matched_count = 0
        
        for recipe_ing in recipe_ingredients:
            recipe_ing_lower = recipe_ing.lower()
            
            for search_ing in search_ingredients:
                if (search_ing in recipe_ing_lower or 
                    recipe_ing_lower.split()[0] in search_ing or
                    search_ing.split()[0] in recipe_ing_lower):
                    matched_count += 1
                    break
        
        score = (matched_count / len(recipe_ingredients)) * 100
        return round(score)
    
    def _get_matched_ingredients(self, search_ingredients, recipe_ingredients):
        """Get list of ingredients that match"""
        matched = []
        
        for search_ing in search_ingredients:
            for recipe_ing in recipe_ingredients:
                recipe_ing_lower = recipe_ing.lower()
                
                if (search_ing in recipe_ing_lower or 
                    recipe_ing_lower.split()[0] in search_ing or
                    search_ing.split()[0] in recipe_ing_lower):
                    matched.append(search_ing)
                    break
        
        return matched
    
    def _get_missing_ingredients(self, search_ingredients, recipe_ingredients):
        """Get list of ingredients user doesn't have"""
        missing = []
        
        for recipe_ing in recipe_ingredients:
            recipe_ing_lower = recipe_ing.lower()
            found = False
            
            for search_ing in search_ingredients:
                if (search_ing in recipe_ing_lower or 
                    recipe_ing_lower.split()[0] in search_ing or
                    search_ing.split()[0] in recipe_ing_lower):
                    found = True
                    break
            
            if not found:
                # Extract main ingredient
                main_ingredient = recipe_ing.split(',')[0].strip()
                words = main_ingredient.split()
                clean = ' '.join([w for w in words if not any(c.isdigit() for c in w)])
                
                if clean and len(clean) > 2:
                    missing.append(clean)
        
        return missing[:5]
    
    def _estimate_cooking_time(self, recipe_name):
        """Estimate cooking time based on recipe name"""
        quick_recipes = ['sambol', 'roti', 'egg']
        medium_recipes = ['curry', 'fish', 'vegetable']
        long_recipes = ['hoppers', 'string']
        
        name_lower = recipe_name.lower()
        
        if any(quick in name_lower for quick in quick_recipes):
            return '15-20 mins'
        elif any(long in name_lower for long in long_recipes):
            return '1-2 hours'
        else:
            return '30-45 mins'
    
    def _estimate_difficulty(self, recipe_name):
        """Estimate difficulty based on recipe name"""
        easy = ['sambol', 'rice', 'egg roti']
        hard = ['hoppers', 'string', 'kottu']
        
        name_lower = recipe_name.lower()
        
        if any(e in name_lower for e in easy):
            return 'Easy'
        elif any(h in name_lower for h in hard):
            return 'Hard'
        else:
            return 'Medium'


# Global instance
_rag_instance = None

def get_rag_model():
    """Get or create RAG model instance"""
    global _rag_instance
    
    if _rag_instance is None:
        _rag_instance = SriLankanRecipeRAG()
        
        # Load recipes on first initialization
        success = _rag_instance.load_recipes_from_folder()
        
        if not success:
            print("⚠️ Failed to load recipes.")
    
    return _rag_instance