"""
AI-Powered Product Recommendation Engine
Uses OpenAI and ML to provide personalized product recommendations
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
import json


class RecommendationEngine:
    """AI-powered recommendation engine"""
    
    def __init__(self):
        self.openai_client = None
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"OpenAI initialization error: {str(e)}")
    
    def generate_recommendations(
        self,
        products: List[Dict],
        user_preferences: Optional[Dict] = None,
        search_history: Optional[List[str]] = None,
        budget: Optional[float] = None
    ) -> List[Dict]:
        """
        Generate AI-powered recommendations from product list
        """
        if not products:
            return []
        
        # If OpenAI is available, use it for intelligent recommendations
        if self.openai_client:
            return self._ai_recommend(products, user_preferences, search_history, budget)
        else:
            # Fallback to rule-based recommendations
            return self._rule_based_recommend(products, user_preferences, budget)
    
    def _ai_recommend(
        self,
        products: List[Dict],
        user_preferences: Optional[Dict],
        search_history: Optional[List[str]],
        budget: Optional[float]
    ) -> List[Dict]:
        """Use OpenAI to generate intelligent recommendations"""
        try:
            # Prepare context
            product_summary = []
            for p in products[:10]:  # Limit to top 10 for context
                product_summary.append({
                    'name': p.get('name', ''),
                    'price': p.get('price', 0),
                    'rating': p.get('rating', 0),
                    'category': p.get('category', ''),
                    'platform': p.get('platform', '')
                })
            
            context = f"""
            User is searching for products. Here are available products:
            {json.dumps(product_summary, indent=2)}
            
            User preferences: {json.dumps(user_preferences or {})}
            Recent searches: {', '.join(search_history[-5:]) if search_history else 'None'}
            Budget: ${budget if budget else 'Not specified'}
            
            Analyze these products and recommend the top 5-8 best options considering:
            1. Value for money (price vs rating)
            2. User preferences and search history
            3. Budget constraints
            4. Product quality indicators
            
            Return a JSON array with product recommendations, each with:
            - product_index: index in original list
            - ai_reason: brief explanation why this product is recommended
            - score: recommendation score (0-100)
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert shopping assistant. Provide product recommendations in JSON format."},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI response
            content = response.choices[0].message.content
            # Try to extract JSON from response
            try:
                # Find JSON in response
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    recommendations = json.loads(content[json_start:json_end])
                    
                    # Apply recommendations to products
                    recommended_products = []
                    for rec in recommendations[:8]:
                        idx = rec.get('product_index', 0)
                        if 0 <= idx < len(products):
                            product = products[idx].copy()
                            product['aiReason'] = rec.get('ai_reason', 'AI recommended based on your preferences')
                            product['recommendation_score'] = rec.get('score', 75)
                            recommended_products.append(product)
                    
                    # Sort by recommendation score
                    recommended_products.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
                    return recommended_products
            except:
                pass
            
            # Fallback if JSON parsing fails
            return self._rule_based_recommend(products, user_preferences, budget)
            
        except Exception as e:
            print(f"OpenAI recommendation error: {str(e)}")
            return self._rule_based_recommend(products, user_preferences, budget)
    
    def _rule_based_recommend(
        self,
        products: List[Dict],
        user_preferences: Optional[Dict],
        budget: Optional[float]
    ) -> List[Dict]:
        """Rule-based recommendation system (fallback)"""
        if not products:
            return []
        
        # Score products
        scored_products = []
        for product in products:
            score = 0
            
            # Rating score (0-40 points)
            rating = product.get('rating', 0)
            score += rating * 8
            
            # Price score (0-30 points) - lower price gets higher score if within budget
            price = product.get('price', 0)
            if budget:
                if price <= budget:
                    score += 30 * (1 - (price / budget))
                else:
                    score -= 10  # Penalty for over budget
            else:
                # If no budget, prefer mid-range prices
                avg_price = sum(p.get('price', 0) for p in products) / len(products)
                if price <= avg_price * 1.2:
                    score += 20
            
            # Platform diversity (0-10 points)
            platform = product.get('platform', '')
            if platform in ['eBay', 'Amazon', 'Walmart']:
                score += 10
            
            # Availability (0-10 points)
            if product.get('availability', '').lower() == 'in stock':
                score += 10
            
            # Category match (0-10 points)
            if user_preferences and 'category' in user_preferences:
                if product.get('category', '') == user_preferences['category']:
                    score += 10
            
            product_copy = product.copy()
            product_copy['recommendation_score'] = score
            
            # Generate AI reason
            reasons = []
            if rating >= 4.5:
                reasons.append("highly rated")
            if price <= (budget or 100) * 0.7:
                reasons.append("great value")
            if platform in ['Amazon', 'eBay']:
                reasons.append(f"from trusted platform {platform}")
            
            product_copy['aiReason'] = f"Recommended because it's {', '.join(reasons) if reasons else 'a good option based on your search'}"
            scored_products.append(product_copy)
        
        # Sort by score and return top products
        scored_products.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        # Add recommendation reasons to top products
        return scored_products[:10]  # Return top 10

