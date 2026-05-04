"""
Recipe Chunker - splits raw cookbook text into individual recipe chunks
"""

import re
from typing import List

class RecipeChunker:
    """Splits raw text into individual recipe chunks"""
    
    # Patterns that typically indicate the start of a new recipe
    RECIPE_START_PATTERNS = [
        r'^\#{1,3}\s+\w+',           # Markdown headers: # Recipe Name
        r'^\d+\.\s+[A-Z][a-z]+',     # Numbered: 1. Chicken Curry
        r'^[A-Z][A-Z\s]{3,40}$',     # ALL CAPS TITLE
        r'^Recipe\s*:\s*\w+',         # Recipe: Name
    ]
    
    def __init__(self, min_chunk_length: int = 50, max_chunk_length: int = 3000):
        """
        Args:
            min_chunk_length: Minimum characters for a valid recipe chunk
            max_chunk_length: Maximum characters before forcibly splitting
        """
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
    
    def chunk(self, text: str) -> List[str]:
        """
        Split cookbook text into individual recipe chunks
        
        Args:
            text: Full cookbook text
            
        Returns:
            List of recipe text chunks
        """
        # Try pattern-based splitting first
        chunks = self._split_by_patterns(text)
        
        # If that gives too few results, try double-newline splitting
        if len(chunks) < 3:
            chunks = self._split_by_newlines(text)
        
        # Filter and clean chunks
        chunks = self._filter_chunks(chunks)
        
        return chunks
    
    def _split_by_patterns(self, text: str) -> List[str]:
        """Split text by recipe header patterns"""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        
        compiled_patterns = [re.compile(p, re.MULTILINE) for p in self.RECIPE_START_PATTERNS]
        
        for line in lines:
            is_header = any(p.match(line.strip()) for p in compiled_patterns)
            
            if is_header and current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
        
        return chunks
    
    def _split_by_newlines(self, text: str) -> List[str]:
        """Split by double newlines as fallback"""
        raw_chunks = re.split(r'\n\s*\n\s*\n', text)
        return [c.strip() for c in raw_chunks if c.strip()]
    
    def _filter_chunks(self, chunks: List[str]) -> List[str]:
        """
        Remove chunks that are too short, too long,
        or don't look like recipes
        """
        filtered = []
        
        for chunk in chunks:
            # Too short
            if len(chunk) < self.min_chunk_length:
                continue
            
            # Too long — split further
            if len(chunk) > self.max_chunk_length:
                sub_chunks = self._split_long_chunk(chunk)
                filtered.extend(sub_chunks)
                continue
            
            # Must contain at least some ingredient/cooking keywords
            has_recipe_content = any(
                kw in chunk.lower() for kw in [
                    'ingredient', 'cup', 'tsp', 'tbsp', 'gram',
                    'mix', 'cook', 'boil', 'fry', 'add', 'stir',
                    'heat', 'serve', 'method', 'step',
                ]
            )
            
            if has_recipe_content:
                filtered.append(chunk)
        
        return filtered
    
    def _split_long_chunk(self, chunk: str) -> List[str]:
        """Split an oversized chunk into smaller pieces"""
        parts = re.split(r'\n\s*\n', chunk)
        result = []
        current = ""
        
        for part in parts:
            if len(current) + len(part) < self.max_chunk_length:
                current += "\n\n" + part
            else:
                if current.strip():
                    result.append(current.strip())
                current = part
        
        if current.strip():
            result.append(current.strip())
        
        return result