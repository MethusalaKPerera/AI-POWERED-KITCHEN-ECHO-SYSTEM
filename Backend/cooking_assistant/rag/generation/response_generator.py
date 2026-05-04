"""
Response Generator - uses Claude API to generate natural language
recipe recommendations from retrieved results
"""

import os
import json
import requests
from typing import List, Dict, Any

class ResponseGenerator:
    """Generates natural language responses using Claude API"""
    
    CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-sonnet-4-20250514"
    
    def __init__(self):
        """Initialize generator — API key handled by environment"""
        print("✓ Response Generator initialized")
    
    def generate_recommendation(
        self,
        user_ingredients: List[str],
        retrieved_recipes: List[Dict[str, Any]],
        user_preferences: Dict[str, Any] = None,
        conversation_history: List[Dict] = None,
    ) -> str:
        """
        Generate a natural language recipe recommendation
        
        Args:
            user_ingredients: What the user has
            retrieved_recipes: Top recipes from semantic search
            user_preferences: Optional dict (dietary, spice level etc)
            conversation_history: Past messages for context
            
        Returns:
            Natural language recommendation string
        """
        if not retrieved_recipes:
            return "I couldn't find any recipes matching your ingredients. Try adding more ingredients!"
        
        # Build context from retrieved recipes
        recipes_context = self._format_recipes_for_prompt(retrieved_recipes[:5])
        
        # Build preferences string
        prefs_str = ""
        if user_preferences:
            prefs_str = f"\nUser preferences: {json.dumps(user_preferences)}"
        
        # Build the prompt
        prompt = f"""You are a helpful cooking assistant. A user has these ingredients available:
{', '.join(user_ingredients)}
{prefs_str}

Based on a recipe search, here are the top matching recipes:

{recipes_context}

Please provide a helpful, conversational recommendation. For each recipe:
1. Explain WHY it matches their ingredients
2. Mention which ingredients they already have vs what they're missing
3. Give a brief tip about the recipe
4. Be encouraging and friendly

Keep your response concise and practical."""

        # Build messages including conversation history
        messages = []
        
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges
        
        messages.append({"role": "user", "content": prompt})
        
        return self._call_claude(messages)
    
    def generate_substitution(
        self,
        missing_ingredient: str,
        recipe_name: str,
        available_ingredients: List[str],
    ) -> str:
        """
        Suggest substitutions for a missing ingredient
        
        Args:
            missing_ingredient: What the user doesn't have
            recipe_name: The recipe they want to make
            available_ingredients: What they do have
            
        Returns:
            Substitution suggestion string
        """
        prompt = f"""A user wants to make "{recipe_name}" but doesn't have "{missing_ingredient}".

They have available: {', '.join(available_ingredients)}

Suggest the best substitution from what they have, or a common pantry substitute.
Be specific about quantities if the substitution ratio differs.
Keep it to 2-3 sentences."""

        messages = [{"role": "user", "content": prompt}]
        return self._call_claude(messages)
    
    def generate_cooking_tip(
        self,
        recipe_name: str,
        recipe_instructions: str,
        user_question: str,
    ) -> str:
        """
        Answer a specific question about cooking a recipe
        
        Args:
            recipe_name: Name of the recipe
            recipe_instructions: Full instructions
            user_question: What the user wants to know
            
        Returns:
            Helpful cooking tip or answer
        """
        prompt = f"""Recipe: {recipe_name}

Instructions:
{recipe_instructions[:1000]}

User question: {user_question}

Answer helpfully and concisely based on the recipe above."""

        messages = [{"role": "user", "content": prompt}]
        return self._call_claude(messages)
    
    def _format_recipes_for_prompt(self, recipes: List[Dict[str, Any]]) -> str:
        """Format retrieved recipes into readable prompt context"""
        formatted = []
        
        for i, recipe in enumerate(recipes, 1):
            matched = recipe.get('matched_ingredients', [])
            missing = recipe.get('missing_ingredients', [])
            score = recipe.get('match_score', 0)
            
            text = f"""Recipe {i}: {recipe.get('name', 'Unknown')}
- Match Score: {score}%
- Category: {recipe.get('category', 'General')}
- Difficulty: {recipe.get('difficulty', 'medium')}
- Cooking Time: {recipe.get('cooking_time', '40 mins')}
- Ingredients you have: {', '.join(matched[:6]) if matched else 'None detected'}
- Ingredients you need: {', '.join(missing[:5]) if missing else 'None'}"""
            
            formatted.append(text)
        
        return '\n\n'.join(formatted)
    
    def _call_claude(self, messages: List[Dict]) -> str:
        """
        Make API call to Claude
        
        Args:
            messages: Message history
            
        Returns:
            Claude's response text
        """
        try:
            response = requests.post(
                self.CLAUDE_API_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.MODEL,
                    "max_tokens": 1000,
                    "messages": messages,
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['content'][0]['text']
            else:
                print(f"⚠ Claude API error: {response.status_code}")
                return self._fallback_response(messages)
                
        except Exception as e:
            print(f"⚠ Generation error: {e}")
            return self._fallback_response(messages)
    
    def _fallback_response(self, messages: List[Dict]) -> str:
        """Simple fallback if Claude API is unavailable"""
        return "Here are your top recipe matches based on your ingredients. Check the match scores to find the best fit!"