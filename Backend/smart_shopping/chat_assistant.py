"""
Context-Aware Chat Assistant
Uses OpenAI to provide intelligent shopping assistance
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
import json


class ChatAssistant:
    """AI-powered chat assistant for shopping guidance"""
    
    def __init__(self):
        self.openai_client = None
        self.conversation_history = []
        
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"OpenAI initialization error: {str(e)}")
    
    def get_response(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        search_history: Optional[List[str]] = None
    ) -> str:
        """
        Generate context-aware response to user query
        """
        if not user_message or not user_message.strip():
            return "I'm here to help you with your shopping needs! What are you looking for?"
        
        # If OpenAI is available, use it
        if self.openai_client:
            return self._ai_response(user_message, context, search_history)
        else:
            return self._rule_based_response(user_message, context)
    
    def _ai_response(
        self,
        user_message: str,
        context: Optional[Dict],
        search_history: Optional[List[str]]
    ) -> str:
        """Generate AI-powered response using OpenAI"""
        try:
            system_prompt = """You are a helpful AI shopping assistant. Your role is to:
1. Help users find products they're looking for
2. Provide shopping advice and recommendations
3. Answer questions about products, prices, and shopping
4. Be friendly, concise, and helpful

Keep responses brief (1-2 sentences) and actionable."""
            
            # Build context
            context_info = ""
            if context:
                context_info += f"\nCurrent search context: {json.dumps(context, indent=2)}"
            if search_history:
                context_info += f"\nUser's recent searches: {', '.join(search_history[-3:])}"
            
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            # Add recent conversation history (last 3 messages)
            if len(self.conversation_history) > 0:
                messages.extend(self.conversation_history[-6:])  # Last 3 exchanges
            
            messages.append({
                "role": "user",
                "content": user_message + context_info
            })
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep history limited to last 10 messages
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return ai_response
            
        except Exception as e:
            print(f"OpenAI chat error: {str(e)}")
            return self._rule_based_response(user_message, context)
    
    def _rule_based_response(
        self,
        user_message: str,
        context: Optional[Dict]
    ) -> str:
        """Rule-based response (fallback)"""
        message_lower = user_message.lower()
        
        # Budget questions
        if any(word in message_lower for word in ['budget', 'cheap', 'affordable', 'price']):
            return "I can help you find products within your budget! Try using the price filter or let me know your budget range, and I'll recommend the best options for you."
        
        # Recommendation questions
        if any(word in message_lower for word in ['recommend', 'suggest', 'best', 'good']):
            return "I'd be happy to recommend products! Use the search feature and I'll show you AI-powered recommendations based on ratings, prices, and your preferences."
        
        # Comparison questions
        if any(word in message_lower for word in ['compare', 'difference', 'vs', 'versus']):
            return "You can compare products by viewing their details side by side. Search for products and I'll help you find the best options with price comparisons across different platforms."
        
        # General help
        if any(word in message_lower for word in ['help', 'how', 'what', 'where']):
            return "I'm here to help! You can search for products using voice or text, filter by price and category, and get AI-powered recommendations. What would you like to find?"
        
        # Default response
        return "I can help you find products, compare prices, and get recommendations! Try searching for what you're looking for, or ask me about specific products or features."
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

