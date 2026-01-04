"""
NLP Query Processing
Uses SpaCy to extract keywords and understand user intent from search queries
"""
import spacy
from typing import Dict, List, Optional
import re


class NLPProcessor:
    """Processes natural language queries to extract keywords and intent"""
    
    def __init__(self):
        try:
            # Try to load English model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, use basic processing
            print("Warning: spaCy model 'en_core_web_sm' not found. Using basic NLP.")
            self.nlp = None
    
    def process_query(self, query: str) -> Dict:
        """
        Process user query to extract:
        - Keywords
        - Product type
        - Intent (search, compare, recommend)
        - Attributes (brand, color, size, etc.)
        """
        if not query or not query.strip():
            return {
                'keywords': [],
                'product_type': '',
                'intent': 'search',
                'attributes': {},
                'original_query': query
            }
        
        query = query.strip()
        
        if self.nlp:
            return self._process_with_spacy(query)
        else:
            return self._process_basic(query)
    
    def _process_with_spacy(self, query: str) -> Dict:
        """Process query using SpaCy NLP model"""
        doc = self.nlp(query.lower())
        
        # Extract keywords (nouns and important adjectives)
        keywords = []
        product_type = ''
        attributes = {}
        
        for token in doc:
            # Extract nouns as product types
            if token.pos_ == 'NOUN' and not token.is_stop:
                if not product_type:
                    product_type = token.text
                keywords.append(token.text)
            
            # Extract adjectives as attributes
            elif token.pos_ == 'ADJ' and not token.is_stop:
                keywords.append(token.text)
                # Common attributes
                if token.text in ['cheap', 'affordable', 'budget']:
                    attributes['price_range'] = 'low'
                elif token.text in ['premium', 'expensive', 'luxury', 'high-end']:
                    attributes['price_range'] = 'high'
                elif token.text in ['wireless', 'bluetooth', 'smart']:
                    attributes['features'] = attributes.get('features', []) + [token.text]
        
        # Extract intent
        intent = 'search'
        intent_keywords = {
            'compare': ['compare', 'comparison', 'difference', 'vs', 'versus'],
            'recommend': ['recommend', 'suggest', 'best', 'top', 'good'],
            'search': ['find', 'search', 'look', 'show']
        }
        
        query_lower = query.lower()
        for intent_type, keywords_list in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords_list):
                intent = intent_type
                break
        
        # Extract entities (brands, models, etc.)
        entities = {}
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT']:
                entities['brand'] = ent.text
        
        return {
            'keywords': list(set(keywords)),
            'product_type': product_type,
            'intent': intent,
            'attributes': {**attributes, **entities},
            'original_query': query
        }
    
    def _process_basic(self, query: str) -> Dict:
        """Basic processing without SpaCy model"""
        query_lower = query.lower()
        
        # Extract keywords (simple word splitting)
        words = re.findall(r'\b\w+\b', query_lower)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Determine product type (first significant noun)
        product_type = keywords[0] if keywords else ''
        
        # Extract intent
        intent = 'search'
        if any(word in query_lower for word in ['compare', 'vs', 'versus']):
            intent = 'compare'
        elif any(word in query_lower for word in ['recommend', 'suggest', 'best']):
            intent = 'recommend'
        
        # Extract attributes
        attributes = {}
        if any(word in query_lower for word in ['cheap', 'affordable', 'budget']):
            attributes['price_range'] = 'low'
        elif any(word in query_lower for word in ['premium', 'expensive', 'luxury']):
            attributes['price_range'] = 'high'
        
        return {
            'keywords': keywords,
            'product_type': product_type,
            'intent': intent,
            'attributes': attributes,
            'original_query': query
        }
    
    def extract_filters(self, query: str, existing_filters: Optional[Dict] = None) -> Dict:
        """Extract filter parameters from query"""
        processed = self.process_query(query)
        filters = existing_filters or {}
        
        # Extract price mentions
        price_pattern = r'\$?(\d+)\s*(?:to|-)?\s*\$?(\d+)?'
        price_matches = re.findall(price_pattern, query)
        if price_matches:
            min_price = int(price_matches[0][0])
            max_price = int(price_matches[0][1]) if price_matches[0][1] else min_price * 2
            filters['priceRange'] = [min_price, max_price]
        
        # Extract rating mentions
        rating_pattern = r'(\d+)\s*star'
        rating_matches = re.findall(rating_pattern, query.lower())
        if rating_matches:
            filters['rating'] = int(rating_matches[0])
        
        # Extract category mentions
        categories = ['electronics', 'fashion', 'home', 'sports', 'books']
        for category in categories:
            if category in query.lower():
                filters['category'] = category
                break
        
        return filters

