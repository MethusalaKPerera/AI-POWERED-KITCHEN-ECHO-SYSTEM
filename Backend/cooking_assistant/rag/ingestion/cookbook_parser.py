"""
Cookbook Parser - extracts recipes from PDF and text cookbooks
"""

import os
import json
import re
from typing import List, Dict, Any

class CookbookParser:
    """Parses cookbook files (PDF/text) and extracts recipes"""
    
    SUPPORTED_FORMATS = ['.pdf', '.txt', '.md']
    
    def __init__(self, cookbooks_dir: str, output_path: str):
        """
        Args:
            cookbooks_dir: Folder where your cookbook files live
            output_path: Where to save extracted recipes (recipe_database.json)
        """
        self.cookbooks_dir = cookbooks_dir
        self.output_path = output_path
        self.extracted_recipes = []
    
    def parse_all(self) -> List[Dict[str, Any]]:
        """
        Scan cookbooks folder and parse all supported files
        
        Returns:
            List of extracted recipe dicts
        """
        if not os.path.exists(self.cookbooks_dir):
            print(f"⚠ Cookbooks directory not found: {self.cookbooks_dir}")
            return []
        
        files = os.listdir(self.cookbooks_dir)
        supported = [f for f in files if os.path.splitext(f)[1].lower() in self.SUPPORTED_FORMATS]
        
        print(f"Found {len(supported)} cookbook files to parse...")
        
        for filename in supported:
            filepath = os.path.join(self.cookbooks_dir, filename)
            ext = os.path.splitext(filename)[1].lower()
            
            print(f"  Parsing: {filename}")
            
            if ext == '.pdf':
                recipes = self.parse_pdf(filepath)
            elif ext in ['.txt', '.md']:
                recipes = self.parse_text(filepath)
            else:
                continue
            
            print(f"  ✓ Extracted {len(recipes)} recipes from {filename}")
            self.extracted_recipes.extend(recipes)
        
        print(f"\n✓ Total recipes extracted: {len(self.extracted_recipes)}")
        return self.extracted_recipes
    
    def parse_pdf(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Extract recipes from a PDF cookbook
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            List of recipe dicts
        """
        try:
            import pdfplumber
        except ImportError:
            print("  ⚠ pdfplumber not installed. Run: pip install pdfplumber")
            return []
        
        full_text = ""
        
        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception as e:
            print(f"  ✗ Error reading PDF {filepath}: {e}")
            return []
        
        return self._extract_recipes_from_text(full_text, source=os.path.basename(filepath))
    
    def parse_text(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Extract recipes from a plain text or markdown cookbook
        
        Args:
            filepath: Path to text file
            
        Returns:
            List of recipe dicts
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except Exception as e:
            print(f"  ✗ Error reading file {filepath}: {e}")
            return []
        
        return self._extract_recipes_from_text(full_text, source=os.path.basename(filepath))
    
    def _extract_recipes_from_text(self, text: str, source: str = '') -> List[Dict[str, Any]]:
        """
        Parse raw text and extract structured recipe dicts
        
        Args:
            text: Raw text content
            source: Source filename for tracking
            
        Returns:
            List of structured recipe dicts
        """
        from .recipe_chunker import RecipeChunker
        chunker = RecipeChunker()
        chunks = chunker.chunk(text)
        
        recipes = []
        for i, chunk in enumerate(chunks):
            recipe = self._parse_recipe_chunk(chunk, source=source, index=i)
            if recipe:
                recipes.append(recipe)
        
        return recipes
    
    def _parse_recipe_chunk(self, chunk: str, source: str = '', index: int = 0) -> Dict[str, Any]:
        """
        Convert a raw text chunk into a structured recipe dict
        
        Args:
            chunk: Raw text of one recipe
            source: Source filename
            index: Recipe index for ID generation
            
        Returns:
            Structured recipe dict or None if parsing fails
        """
        lines = [l.strip() for l in chunk.strip().split('\n') if l.strip()]
        
        if not lines:
            return None
        
        # First non-empty line = recipe name
        name = lines[0].strip('# ').strip()
        
        if len(name) < 3 or len(name) > 100:
            return None
        
        # Generate unique ID
        safe_name = re.sub(r'[^a-z0-9]', '_', name.lower())
        recipe_id = f"{safe_name}_{index}"
        
        # Extract ingredients section
        ingredients = self._extract_ingredients(chunk)
        
        # Extract instructions section
        instructions = self._extract_instructions(chunk)
        
        # Try to detect category
        category = self._detect_category(name, chunk)
        
        # Try to detect difficulty
        difficulty = self._detect_difficulty(chunk)
        
        return {
            'id': recipe_id,
            'name': name,
            'names': {'english': name},
            'category': category,
            'difficulty': difficulty,
            'ingredients': ingredients,
            'instructions': instructions,
            'servings': self._extract_servings(chunk),
            'prep_time_mins': 15,
            'cook_time_mins': 30,
            'source': source,
        }
    
    def _extract_ingredients(self, text: str) -> List[Dict[str, str]]:
        """Extract ingredients list from recipe text"""
        ingredients = []
        
        # Look for ingredients section
        ing_pattern = re.search(
            r'(?:ingredients?[:\s]*)(.*?)(?:(?:method|instructions?|directions?|steps?)|$)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if ing_pattern:
            ing_text = ing_pattern.group(1)
            lines = ing_text.strip().split('\n')
            
            for line in lines:
                line = line.strip().lstrip('-•*').strip()
                if line and len(line) > 2:
                    ingredients.append({
                        'name': {'english': line},
                        'quantity': '',
                    })
        
        return ingredients
    
    def _extract_instructions(self, text: str) -> str:
        """Extract cooking instructions from recipe text"""
        inst_pattern = re.search(
            r'(?:method|instructions?|directions?|steps?)[:\s]*(.*?)$',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if inst_pattern:
            return inst_pattern.group(1).strip()
        
        return ""
    
    def _detect_category(self, name: str, text: str) -> str:
        """Detect recipe category from name and content"""
        combined = (name + ' ' + text).lower()
        
        if any(w in combined for w in ['curry', 'rice', 'dal', 'dhal', 'sambal']):
            return 'Main Course'
        elif any(w in combined for w in ['cake', 'pudding', 'sweet', 'dessert', 'cookie']):
            return 'Dessert'
        elif any(w in combined for w in ['soup', 'broth', 'stew']):
            return 'Soup'
        elif any(w in combined for w in ['salad', 'sambol']):
            return 'Side Dish'
        elif any(w in combined for w in ['drink', 'juice', 'tea', 'coffee', 'smoothie']):
            return 'Beverage'
        elif any(w in combined for w in ['bread', 'roti', 'hoppers', 'pittu']):
            return 'Bread'
        
        return 'General'
    
    def _detect_difficulty(self, text: str) -> str:
        """Detect difficulty from text hints"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ['easy', 'simple', 'quick', 'beginner']):
            return 'easy'
        elif any(w in text_lower for w in ['advanced', 'complex', 'difficult', 'expert']):
            return 'hard'
        
        return 'medium'
    
    def _extract_servings(self, text: str) -> int:
        """Extract serving size from text"""
        match = re.search(r'serves?\s*:?\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 4
    
    def save_to_database(self, recipes: List[Dict[str, Any]] = None):
        """
        Save extracted recipes to recipe_database.json
        Merges with existing recipes if file exists
        
        Args:
            recipes: Recipes to save (uses self.extracted_recipes if None)
        """
        recipes_to_save = recipes or self.extracted_recipes
        
        # Load existing database if it exists
        existing = []
        if os.path.exists(self.output_path):
            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing = data if isinstance(data, list) else data.get('recipes', [])
                print(f"Found {len(existing)} existing recipes in database")
            except Exception:
                existing = []
        
        # Merge - avoid duplicates by ID
        existing_ids = {r.get('id') for r in existing}
        new_recipes = [r for r in recipes_to_save if r.get('id') not in existing_ids]
        
        merged = existing + new_recipes
        
        # Save
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(merged)} total recipes ({len(new_recipes)} new) to {self.output_path}")