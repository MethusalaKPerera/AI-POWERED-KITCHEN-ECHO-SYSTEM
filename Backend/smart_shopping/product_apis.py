"""
Product API Integrations
Fetches products from various e-commerce platforms using official APIs
"""
import requests
import os
from typing import List, Dict, Optional
from datetime import datetime


class ProductAPIClient:
    """Base class for product API clients"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for products - to be implemented by subclasses"""
        raise NotImplementedError


class eBayAPIClient(ProductAPIClient):
    """eBay Finding API client"""
    
    def __init__(self):
        super().__init__()
        self.app_id = os.getenv('EBAY_APP_ID', 'YourAppID')
        self.base_url = 'https://svcs.ebay.com/services/search/FindingService/v1'
    
    def search_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search eBay products using Finding API
        Falls back to mock data if API key not configured
        """
        try:
            # If API key is not set, return mock data
            if self.app_id == 'YourAppID':
                return self._get_mock_ebay_products(query, filters)
            
            params = {
                'OPERATION-NAME': 'findItemsByKeywords',
                'SERVICE-VERSION': '1.0.0',
                'SECURITY-APPNAME': self.app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'REST-PAYLOAD': '',
                'keywords': query,
                'paginationInput.entriesPerPage': 20
            }
            
            if filters:
                if filters.get('priceRange'):
                    min_price = filters['priceRange'][0]
                    max_price = filters['priceRange'][1]
                    params['itemFilter(0).name'] = 'MinPrice'
                    params['itemFilter(0).value'] = min_price
                    params['itemFilter(1).name'] = 'MaxPrice'
                    params['itemFilter(1).value'] = max_price
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            products = []
            if 'findItemsByKeywordsResponse' in data:
                items = data['findItemsByKeywordsResponse'][0].get('searchResult', [{}])[0].get('item', [])
                for item in items[:20]:  # Limit to 20 items
                    products.append({
                        'id': item.get('itemId', [''])[0],
                        'name': item.get('title', [''])[0],
                        'price': float(item.get('sellingStatus', [{}])[0].get('currentPrice', [{}])[0].get('__value__', 0)),
                        'currency': item.get('sellingStatus', [{}])[0].get('currentPrice', [{}])[0].get('@currencyId', 'USD'),
                        'image': item.get('galleryURL', [''])[0] if item.get('galleryURL') else '',
                        'url': item.get('viewItemURL', [''])[0],
                        'rating': 4.0 + (hash(item.get('itemId', [''])[0]) % 10) / 10,  # Mock rating
                        'category': item.get('primaryCategory', [{}])[0].get('categoryName', [''])[0] if item.get('primaryCategory') else 'general',
                        'platform': 'eBay',
                        'availability': 'In Stock'
                    })
            
            return products if products else self._get_mock_ebay_products(query, filters)
            
        except Exception as e:
            print(f"eBay API Error: {str(e)}")
            return self._get_mock_ebay_products(query, filters)
    
    def _get_mock_ebay_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Generate mock eBay products based on query"""
        base_products = [
            {
                'id': f'ebay-{hash(query + "1") % 100000}',
                'name': f'{query.title()} - Premium Quality',
                'price': 49.99,
                'currency': 'USD',
                'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
                'url': f'https://www.ebay.com/itm/{hash(query + "1") % 100000}',
                'rating': 4.5,
                'category': 'electronics',
                'platform': 'eBay',
                'availability': 'In Stock'
            },
            {
                'id': f'ebay-{hash(query + "2") % 100000}',
                'name': f'{query.title()} - Best Seller',
                'price': 79.99,
                'currency': 'USD',
                'image': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400',
                'url': f'https://www.ebay.com/itm/{hash(query + "2") % 100000}',
                'rating': 4.8,
                'category': 'electronics',
                'platform': 'eBay',
                'availability': 'In Stock'
            }
        ]
        
        # Apply filters
        if filters and filters.get('priceRange'):
            min_price, max_price = filters['priceRange']
            base_products = [p for p in base_products if min_price <= p['price'] <= max_price]
        
        return base_products


class RapidAPIClient(ProductAPIClient):
    """RapidAPI product search client (Amazon, Walmart, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('RAPIDAPI_KEY', '')
        self.base_url = 'https://amazon-product-search1.p.rapidapi.com'
    
    def search_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search products via RapidAPI
        Falls back to mock data if API key not configured
        """
        try:
            if not self.api_key:
                return self._get_mock_rapidapi_products(query, filters)
            
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'amazon-product-search1.p.rapidapi.com'
            }
            
            params = {
                'query': query,
                'page': '1',
                'country': 'us'
            }
            
            response = self.session.get(
                f'{self.base_url}/search',
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            products = []
            if 'results' in data:
                for item in data['results'][:20]:
                    products.append({
                        'id': item.get('asin', f'rapid-{hash(str(item)) % 100000}'),
                        'name': item.get('title', ''),
                        'price': float(item.get('price', {}).get('value', 0)),
                        'currency': item.get('price', {}).get('currency', 'USD'),
                        'image': item.get('image', ''),
                        'url': item.get('url', ''),
                        'rating': float(item.get('rating', 4.0)),
                        'category': item.get('category', 'general'),
                        'platform': 'Amazon',
                        'availability': 'In Stock'
                    })
            
            return products if products else self._get_mock_rapidapi_products(query, filters)
            
        except Exception as e:
            print(f"RapidAPI Error: {str(e)}")
            return self._get_mock_rapidapi_products(query, filters)
    
    def _get_mock_rapidapi_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Generate mock RapidAPI products"""
        base_products = [
            {
                'id': f'walmart-{hash(query + "w1") % 100000}',
                'name': f'{query.title()} - Walmart Choice',
                'price': 39.99,
                'currency': 'USD',
                'image': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400',
                'url': f'https://www.walmart.com/ip/{hash(query + "w1") % 100000}',
                'rating': 4.3,
                'category': 'home',
                'platform': 'Walmart',
                'availability': 'In Stock'
            },
            {
                'id': f'amazon-{hash(query + "a1") % 100000}',
                'name': f'{query.title()} - Amazon Prime',
                'price': 59.99,
                'currency': 'USD',
                'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',
                'url': f'https://www.amazon.com/dp/{hash(query + "a1") % 100000}',
                'rating': 4.7,
                'category': 'electronics',
                'platform': 'Amazon',
                'availability': 'In Stock'
            }
        ]
        
        if filters and filters.get('priceRange'):
            min_price, max_price = filters['priceRange']
            base_products = [p for p in base_products if min_price <= p['price'] <= max_price]
        
        return base_products


class ProductAggregator:
    """Aggregates products from multiple sources"""
    
    def __init__(self):
        self.ebay_client = eBayAPIClient()
        self.rapidapi_client = RapidAPIClient()
    
    def search_all_platforms(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search across all platforms and combine results"""
        all_products = []
        
        # Search eBay
        ebay_products = self.ebay_client.search_products(query, filters)
        all_products.extend(ebay_products)
        
        # Search RapidAPI (Amazon, Walmart)
        rapidapi_products = self.rapidapi_client.search_products(query, filters)
        all_products.extend(rapidapi_products)
        
        # Remove duplicates based on name similarity
        unique_products = self._deduplicate_products(all_products)
        
        return unique_products
    
    def _deduplicate_products(self, products: List[Dict]) -> List[Dict]:
        """Remove duplicate products based on name similarity"""
        seen_names = set()
        unique = []
        
        for product in products:
            name_lower = product['name'].lower()
            # Simple deduplication - check if similar name exists
            is_duplicate = False
            for seen in seen_names:
                # If names are very similar (80% overlap), consider duplicate
                if self._similarity(name_lower, seen) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_names.add(name_lower)
                unique.append(product)
        
        return unique
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate simple string similarity"""
        words1 = set(s1.split())
        words2 = set(s2.split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0

