
import json
import os
import datetime
import traceback
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
import requests
from dotenv import load_dotenv
import re
from extensions import jwt

load_dotenv()

shopping_bp = Blueprint('shopping', __name__)

SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
SERPAPI_ENDPOINT = 'https://serpapi.com/search.json'

# --- HISTORY FILE SETUP ---
HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'shopping_history.json')

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def update_history_item(user_id, item_id, new_query):
    history = load_history()
    updated = False
    for item in history:
        if item['id'] == item_id and item['user_id'] == user_id:
            item['query'] = new_query
            item['timestamp'] = datetime.datetime.utcnow().isoformat()
            updated = True
            break
    if updated:
        save_history(history)
    return updated

def delete_history_item(user_id, item_id):
    history = load_history()
    original_len = len(history)
    history = [h for h in history if not (h['id'] == item_id and h['user_id'] == user_id)]
    if len(history) < original_len:
        save_history(history)
        return True
    return False

def clear_user_history(user_id):
    history = load_history()
    history = [h for h in history if h['user_id'] != user_id]
    save_history(history)
    return True

def append_history(user_id, action_type, query, details=None):
    """
    user_id: str (ID of the logged in user)
    action_type: str ('search' or 'chat')
    query: str (the search text or chat message)
    details: dict (optional extra info like filter settings or result count)
    """
    try:
        if not user_id:
            return
        
        history = load_history()
        
        # Check for duplication (same user, same query, same type within last 5 mins)
        now = datetime.datetime.now(datetime.timezone.utc)
        for item in reversed(history):
            if item['user_id'] == user_id and item['type'] == action_type and item['query'].lower() == query.lower():
                try:
                    ts = datetime.datetime.fromisoformat(item['timestamp'])
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=datetime.timezone.utc)
                    if (now - ts).total_seconds() < 300: # 5 minutes
                        item['timestamp'] = now.isoformat()
                        save_history(history)
                        return
                except:
                    pass
                break # Only check the most recent match
        
        new_entry = {
            'id': str(len(history) + 1),
            'user_id': user_id,
            'type': action_type,
            'query': query,
            'details': details or {},
            'timestamp': now.isoformat()
        }
        
        history.append(new_entry)
        save_history(history)
    except Exception as e:
        print(f"Error saving history: {e}")

# =================================== PRODUCT SEARCH ===================================

def search_google_shopping(query, max_results=20, country='us'):
    if not query:
        return []

    # Map full country names or codes to gl codes
    country_map = {
        'sri lanka': 'lk',
        'lk': 'lk',
        'us': 'us',
        'united states': 'us',
        'uk': 'uk',
        'united kingdom': 'uk',
        'in': 'in',
        'india': 'in',
        'ca': 'ca',
        'canada': 'ca'
    }
    gl = country_map.get(country.lower().strip(), 'us')

    print(f"Searching Google Shopping ({gl}): {query}")
    products = []

    if not SERPAPI_KEY:
        print("No SerpAPI key → using fallback products")
        return get_fallback_products(query)

    try:
        params = {
            'engine': 'google_shopping',
            'q': query,
            'api_key': SERPAPI_KEY,
            'num': '50',
            'hl': 'en',
            'gl': gl
        }
        response = requests.get(SERPAPI_ENDPOINT, params=params, timeout=15)

        if response.status_code == 200:
            items = response.json().get('shopping_results', [])
            for i, item in enumerate(items[:max_results]):
                try:
                    title = item.get('title', 'Unknown Product')
                    price_str = item.get('price', '$0')
                    price_match = re.search(r'[\d,]+\.?\d*', price_str.replace('$', '').replace(',', ''))
                    price = float(price_match.group()) if price_match else 0.0

                    products.append({
                        'id': f"google_{i}",
                        'name': title.split(' - ')[0].split(' | ')[0],  # Clean title
                        'price': price,
                        'rating': item.get('rating', 4.0),
                        'reviews': item.get('reviews', 0),
                        'image': item.get('thumbnail', 'https://via.placeholder.com/300'),
                        'store': item.get('source', 'Online Store'),
                        'url': item.get('link') or item.get('product_link', '#'),
                        'delivery': item.get('delivery', ''),
                        'inStock': True,
                        'freeShipping': 'free' in item.get('delivery', '').lower(),
                        'onSale': item.get('highlighted', False) or 'sale' in title.lower(),
                        'aiReason': f"Found on {item.get('source', 'Google Shopping')} ({gl.upper()})",
                        'description': title
                    })
                except Exception as e:
                    print(f"Error parsing product {i}: {e}")
                    continue
            print(f"Successfully fetched {len(products)} products from {gl.upper()}")
        else:
            print(f"SerpAPI failed: {response.status_code}")
            return get_fallback_products(query)
    except Exception as e:
        print(f"Request error: {e}")
        return get_fallback_products(query)

    return products


def get_fallback_products(query=""):
    fallback = [
        {"name": "Dell XPS 13 (2024)", "price": 1099.99, "store": "Dell", "url": "https://www.dell.com", "image": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500"},
        {"name": "MacBook Air M3", "price": 1099.00, "store": "Apple", "url": "https://apple.com/macbook-air", "image": "https://images.unsplash.com/photo-1544244010-dda8bcc2d7c4?w=500"},
        {"name": "iPhone 15 Pro", "price": 999.00, "store": "Apple", "url": "https://apple.com/iphone", "image": "https://images.unsplash.com/photo-1592750477383-8262c0b2df79?w=500"},
        {"name": "Samsung Galaxy S24 Ultra", "price": 1199.99, "store": "Samsung", "url": "https://samsung.com", "image": "https://images.unsplash.com/photo-1607936854279-55e8a4c64888?w=500"},
        {"name": "Sony WH-1000XM5 Headphones", "price": 399.99, "store": "Amazon", "url": "https://amazon.com", "image": "https://images.unsplash.com/photo-1505740106531-4249ab8c8e3d?w=500"},
        {"name": "Sony WH-1000XM5 Headphones", "price": 399.99, "store": "Amazon", "url": "https://amazon.com", "image": "https://images.unsplash.com/photo-1505740106531-4249ab8c8e3d?w=500"},
    ]
    # Simple relevance filter
    if query:
        query_lower = query.lower()
        relevant = [p for p in fallback if query_lower in p["name"].lower()]
        if relevant:
            fallback = relevant

    products = []
    for i, p in enumerate(fallback):
        products.append({
            'id': f"fb_{i}",
            'name': p["name"],
            'price': p["price"],
            'rating': 4.7,
            'reviews': 1247,
            'image': p["image"],
            'store': p["store"],
            'url': p["url"],
            'inStock': True,
            'freeShipping': True,
            'onSale': False,
            'aiReason': f"Popular option from {p['store']}",
            'description': p["name"]
        })
    return products


# =================================== ROUTES ===================================

@shopping_bp.route('/api/shopping/chat', methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    methods=['POST', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    supports_credentials=True,
)
def chat():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Check for user identity manually to catch logged in users without enforcing it for everyone (optional)
        user_id = None
        try:
             verify_jwt_in_request(optional=True)
             user_id = get_jwt_identity()
        except:
             pass

        msg = request.json.get('message', '').strip()
        if not msg:
            return jsonify({'success': False, 'response': 'Please type a message.'})

        print(f"Chat: {msg}")

        # Save to history if logged in
        if user_id:
             append_history(user_id, 'chat', msg)

        msg_lower = msg.lower()

        # TRY GEMINI (working in 2025)
        gemini_response = None
        if GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)

                # Fetch recent history context if user is logged in
                history_context = ""
                if user_id:
                    user_history = [h for h in load_history() if h['user_id'] == user_id]
                    # Get last 5 actions
                    recent = user_history[-5:] 
                    if recent:
                        history_context = "User's recent activity:\n" + "\n".join([f"- {h['type']}: {h['query']}" for h in recent]) + "\n\n"

                model = genai.GenerativeModel(
                    'models/gemini-flash-latest',
                    system_instruction=f"{history_context}You are a helpful Kitchen Shopping Assistant. "
                                       f"When users ask how to make a dish or for a recipe, your primary job is to generate a comprehensive SHOPPING LIST of ingredients. "
                                       f"Format the shopping list as a Markdown table with columns: Ingredient, Quantity, and Shopping Tip. "
                                       f"Briefly describe the ingredients and suggest the best types to buy (e.g., 'San Marzano tomatoes are best for pasta sauce'). "
                                       f"Keep the cooking instructions very minimal (1-2 sentences) and focus 90% on the shopping aspect. "
                                       f"Always be friendly and encouraging. Context is provided if available: {history_context}"
                )

                # Relax safety settings to prevent "finish_reason: 2" blocks for recipe queries
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
                ]

                response = model.generate_content(
                    msg,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 4000
                    },
                    safety_settings=safety_settings
                )
                
                # Handle blocked responses
                if response.candidates and response.candidates[0].finish_reason == 3: # SAFETY
                     gemini_response = "I'm sorry, I can't provide that specific information for safety reasons, but I can help you find prices for common kitchen staples!"
                elif response.text:
                     print(f"Gemini: {response.text[:80]}...")
                     gemini_response = response.text
            except Exception as e:
                print(f"Gemini failed: {e}")
                # Fallback handled below

        if gemini_response:
             return jsonify({'success': True, 'response': gemini_response})

        # KEYWORD FALLBACK (when Gemini is down or blocked)
        if any(w in msg_lower for w in ['pasta', 'macaroni', 'spaghetti']):
            response = "For a great pasta, I recommend buying Durum Wheat Semolina pasta, extra virgin olive oil, fresh garlic, and some Parmesan cheese. Should I search for the best prices on these for you?"
        elif any(w in msg_lower for w in ['recipe', 'cook', 'make', 'eat', 'food', 'ingredients']):
            response = f"I'd love to help you shop for '{msg}'! Generally, you'll need the fresh produce and key spices. Would you like me to find the best local prices for the main ingredients?"
        elif any(w in msg_lower for w in ['laptop', 'macbook', 'computer', 'notebook']):
            response = "Looking for a laptop? Top picks: MacBook Air M3, Dell XPS 13, Lenovo ThinkPad. What's your budget? Under $800, $1000–$1500, or premium?"
        elif any(w in msg_lower for w in ['phone', 'iphone', 'samsung', 'pixel']):
            response = "Best phones right now: iPhone 15 Pro, Samsung Galaxy S24, Google Pixel 9. Do you prefer iOS or Android?"
        elif any(w in msg_lower for w in ['headphone', 'earbuds', 'airpods', 'sony']):
            response = "Top headphones: Sony WH-1000XM5 (best noise-canceling), AirPods Pro 2, Bose QuietComfort. Want wireless or wired?"
        elif any(w in msg_lower for w in ['price', 'cheap', 'budget', 'deal', 'discount']):
            response = "Tell me your budget and what you're looking for — I’ll find the best deals under your price!"
        elif any(w in msg_lower for w in ['recommend', 'suggest', 'best']):
            response = "Happy to recommend! What are you shopping for? Laptops, phones, headphones, smartwatch, TV...?"
        elif 'compare' in msg_lower:
            response = "Sure! Tell me the two products (e.g., “iPhone vs Pixel” or “XPS vs MacBook”) and I’ll compare them for you."
        elif any(w in msg_lower for w in ['hi', 'hello', 'hey']):
            response = "Hey there! I'm your AI shopping assistant. Ready to find you the best deals! What are you looking for today?"
        elif 'thank' in msg_lower:
            response = "You're very welcome! Happy shopping — come back anytime!"
        else:
            response = "I'm here to help you shop smarter! Try asking about laptops, phones, prices, or recommendations. What would you like to explore?"

        return jsonify({'success': True, 'response': response})

    except Exception as e:
        print(f"Chat error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'response': 'Oops! Something went wrong. Try again!'}), 500


@shopping_bp.route('/api/shopping/search', methods=['GET', 'OPTIONS'])
@cross_origin(
    origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    methods=['GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    supports_credentials=True,
)
def search_products():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        query = request.args.get('q', '').strip()
        page = max(1, int(request.args.get('page', 1)))
        page_size = int(request.args.get('pageSize', 12))
        min_price = float(request.args.get('minPrice', 0))
        max_price = float(request.args.get('maxPrice', 100000))
        country = request.args.get('country', 'us')

        # Check for user identity manually
        user_id = None
        try:
             verify_jwt_in_request(optional=True)
             user_id = get_jwt_identity()
        except:
             pass
        
        # Save to history if logged in and has query
        if user_id and query:
             append_history(user_id, 'search', query, {'page': page, 'min_price': min_price, 'country': country})

        products = search_google_shopping(query, 100, country) if query else []

        # Price filter
        filtered = [p for p in products if min_price <= p['price'] <= max_price]

        # Pagination
        start = (page - 1) * page_size
        paginated = filtered[start:start + page_size]

        return jsonify({
            'success': True,
            'products': paginated,
            'total': len(filtered),
            'page': page,
            'pageSize': page_size,
            'totalPages': (len(filtered) + page_size - 1) // page_size
        })

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@shopping_bp.route('/api/shopping/recommendations', methods=['GET', 'OPTIONS'])
@cross_origin(
    origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    methods=['GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    supports_credentials=True,
)
def get_recommendations():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        user_id = None
        try:
             verify_jwt_in_request(optional=True)
             user_id = get_jwt_identity()
        except:
             pass
        
        # Default category if no history
        recommended_query = "latest electronics"
        
        if user_id:
            history = load_history()
            # Filter for searches by this user
            user_history = [h for h in history if h['user_id'] == user_id and h['type'] == 'search']
            
            if user_history:
                # Sort by timestamp descending (newest first)
                user_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Get unique recent queries (up to 3)
                seen_queries = set()
                top_queries = []
                for h in user_history:
                    q = h['query'].lower().strip()
                    if q and q not in seen_queries:
                        seen_queries.add(q)
                        top_queries.append(h['query'])
                    if len(top_queries) >= 3:
                        break
                
                if top_queries:
                    all_recommended_products = []
                    # Fetch 4 products for each of the top 3 queries
                    for q in top_queries:
                        query_products = search_google_shopping(q, 4)
                        for p in query_products:
                            p['recommended_by'] = q # Add metadata about why this was picked
                        all_recommended_products.extend(query_products)
                    
                    # Shuffle to mix them up
                    import random
                    random.shuffle(all_recommended_products)
                    
                    reason_str = f"Based on your recent interest in {top_queries[0]}"
                    if len(top_queries) > 1:
                        others = " and " + " & ".join(top_queries[1:])
                        reason_str += others

                    return jsonify({
                        'success': True,
                        'recommendations': all_recommended_products,
                        'reason': reason_str,
                        'source_queries': top_queries
                    })

        # Fallback if no user history found or no user logged in
        products = search_google_shopping(recommended_query, 8)
        
        return jsonify({
            'success': True,
            'recommendations': products,
            'reason': "Popular today"
        })

    except Exception as e:
        print(f"Recommendations error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@shopping_bp.route('/api/shopping/product/<product_id>', methods=['GET', 'OPTIONS'])
@cross_origin(
    origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    methods=['GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    supports_credentials=True,
)
def get_product(product_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # In a real app, you'd fetch from a DB or specific API
        # For this demo, we'll extract the name from the ID if it's a fallback ID or just return a generic search result
        # Most of our IDs are google_0, google_1 etc. which aren't very useful alone.
        # So we might just return a mock or a search result for "product"
        
        # If we had a real product DB, we'd use product_id here.
        # For now, let's return a detailed mock based on common types
        
        return jsonify({
            'success': True,
            'product': {
                'id': product_id,
                'name': "Premium Product",
                'price': 299.99,
                'description': "This is a detailed description of the premium product you selected. It features high-quality materials, advanced technology, and a sleek design that fits any lifestyle.",
                'specs': [
                    {'label': 'Material', 'value': 'Aerospace Grade Aluminum'},
                    {'label': 'Warranty', 'value': '2 Years International'},
                    {'label': 'Weight', 'value': '1.2 kg'}
                ],
                'rating': 4.8,
                'reviews': 156,
                'image': "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800",
                'store': "Official Store",
                'inStock': True,
                'delivery': "Ships in 24 hours"
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@shopping_bp.route('/api/shopping/history', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@cross_origin(
    origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    supports_credentials=True,
)
@jwt_required()
def shopping_history():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        user_id = get_jwt_identity()
        
        if request.method == 'POST':
            # Manual save
            data = request.get_json()
            query = data.get('query')
            if query:
                append_history(user_id, 'search', query, data)
                return jsonify({'success': True, 'message': 'History saved'})
            return jsonify({'success': False, 'error': 'No query provided'}), 400

        if request.method == 'PUT':
            data = request.get_json()
            item_id = data.get('id')
            new_query = data.get('query')
            if item_id and new_query:
                if update_history_item(user_id, item_id, new_query):
                    return jsonify({'success': True, 'message': 'History updated'})
                return jsonify({'success': False, 'error': 'Item not found'}), 404
            return jsonify({'success': False, 'error': 'Missing id or query'}), 400

        if request.method == 'DELETE':
            item_id = request.args.get('id')
            if item_id:
                if delete_history_item(user_id, item_id):
                    return jsonify({'success': True, 'message': 'Item deleted'})
                return jsonify({'success': False, 'error': 'Item not found'}), 404
            
            # Clear all if no ID provided (optional, or separate endpoint)
            if request.args.get('clear_all') == 'true':
                 clear_user_history(user_id)
                 return jsonify({'success': True, 'message': 'History cleared'})
                 
            return jsonify({'success': False, 'error': 'No id provided'}), 400

        # GET method
        all_history = load_history()
        user_history = [h for h in all_history if h['user_id'] == user_id]
        # Sort by timestamp desc
        user_history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(user_history), 200

    except Exception as e:
        print(f"History error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
