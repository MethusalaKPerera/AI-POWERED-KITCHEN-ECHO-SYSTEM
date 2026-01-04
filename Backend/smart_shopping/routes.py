"""
Flask Routes for Smart Shopping Module
"""
from flask import Blueprint, request, jsonify
from .product_apis import ProductAggregator
from .nlp_processor import NLPProcessor
from .recommendation_engine import RecommendationEngine
from .currency_converter import CurrencyConverter
from .chat_assistant import ChatAssistant
from .history_manager import HistoryManager
from datetime import datetime

smart_shopping_bp = Blueprint('smart_shopping', __name__)

# Initialize components
product_aggregator = ProductAggregator()
nlp_processor = NLPProcessor()
recommendation_engine = RecommendationEngine()
currency_converter = CurrencyConverter()
chat_assistant = ChatAssistant()

# History manager will be initialized with mongo_db
history_manager = None


def init_history_manager(mongo_db):
    """Initialize history manager with MongoDB"""
    global history_manager
    history_manager = HistoryManager(mongo_db)


@smart_shopping_bp.route('/search', methods=['POST'])
def search_products():
    """Search products across multiple platforms"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        filters = data.get('filters', {})
        currency = data.get('currency', 'USD')
        user_id = data.get('user_id', 'default_user')
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Search query is required'
            }), 400
        
        # Process query with NLP
        nlp_result = nlp_processor.process_query(query)
        
        # Merge NLP-extracted filters with user filters
        nlp_filters = nlp_processor.extract_filters(query, filters)
        combined_filters = {**filters, **nlp_filters}
        
        # Search products from all platforms
        products = product_aggregator.search_all_platforms(query, combined_filters)
        
        # Convert currency
        if currency != 'USD':
            products = currency_converter.convert_product_prices(products, currency)
        
        # Generate AI recommendations
        search_history = []
        if history_manager:
            history = history_manager.get_history(user_id, limit=10)
            search_history = [h.get('query', '') for h in history]
        
        recommended_products = recommendation_engine.generate_recommendations(
            products,
            user_preferences=combined_filters,
            search_history=search_history,
            budget=combined_filters.get('priceRange', [0, 1000])[1] if combined_filters.get('priceRange') else None
        )
        
        # Save to history
        if history_manager:
            history_manager.add_search(
                user_id=user_id,
                query=query,
                filters=combined_filters,
                results_count=len(recommended_products)
            )
        
        return jsonify({
            'status': 'success',
            'data': {
                'products': recommended_products,
                'total': len(recommended_products),
                'query': query,
                'nlp_analysis': nlp_result,
                'filters_applied': combined_filters
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@smart_shopping_bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Get personalized product recommendations"""
    try:
        data = request.get_json()
        user_preferences = data.get('preferences', {})
        search_history_queries = data.get('search_history', [])
        budget = data.get('budget')
        currency = data.get('currency', 'USD')
        category = data.get('category', '')
        
        # Build search query from preferences
        query_parts = []
        if category:
            query_parts.append(category)
        if user_preferences.get('keywords'):
            query_parts.extend(user_preferences['keywords'])
        query = ' '.join(query_parts) if query_parts else 'best products'
        
        # Search products
        filters = {}
        if budget:
            filters['priceRange'] = [0, budget]
        if category:
            filters['category'] = category
        
        products = product_aggregator.search_all_platforms(query, filters)
        
        # Convert currency
        if currency != 'USD':
            products = currency_converter.convert_product_prices(products, currency)
        
        # Generate recommendations
        recommended = recommendation_engine.generate_recommendations(
            products,
            user_preferences=user_preferences,
            search_history=search_history_queries,
            budget=budget
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': recommended,
                'total': len(recommended)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@smart_shopping_bp.route('/chat', methods=['POST'])
def chat():
    """Chat with AI assistant"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default_user')
        context = data.get('context', {})
        
        if not message:
            return jsonify({
                'status': 'error',
                'message': 'Message is required'
            }), 400
        
        # Get search history for context
        search_history = []
        if history_manager:
            history = history_manager.get_history(user_id, limit=5)
            search_history = [h.get('query', '') for h in history]
        
        # Get AI response
        response = chat_assistant.get_response(
            message,
            context=context,
            search_history=search_history
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'response': response,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@smart_shopping_bp.route('/history', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_history():
    """Manage search history"""
    if not history_manager:
        return jsonify({
            'status': 'error',
            'message': 'History manager not initialized'
        }), 500
    
    try:
        user_id = request.args.get('user_id') or request.json.get('user_id', 'default_user') if request.is_json else 'default_user'
        
        if request.method == 'GET':
            # Get history
            limit = int(request.args.get('limit', 50))
            skip = int(request.args.get('skip', 0))
            search_term = request.args.get('search', '')
            
            if search_term:
                history = history_manager.search_history(user_id, search_term, limit)
            else:
                history = history_manager.get_history(user_id, limit, skip)
            
            return jsonify({
                'status': 'success',
                'data': history,
                'total': len(history)
            }), 200
        
        elif request.method == 'POST':
            # Add to history
            data = request.get_json()
            query = data.get('query', '')
            filters = data.get('filters', {})
            
            result = history_manager.add_search(user_id, query, filters)
            return jsonify(result), 200
        
        elif request.method == 'PUT':
            # Update history
            data = request.get_json()
            search_id = data.get('id')
            query = data.get('query')
            filters = data.get('filters')
            
            result = history_manager.update_search(search_id, query, filters)
            return jsonify(result), 200
        
        elif request.method == 'DELETE':
            # Delete history
            search_id = request.args.get('id')
            
            if search_id:
                result = history_manager.delete_search(search_id, user_id)
            else:
                result = history_manager.clear_history(user_id)
            
            return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@smart_shopping_bp.route('/process-query', methods=['POST'])
def process_query():
    """Process query with NLP"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400
        
        # Process with NLP
        nlp_result = nlp_processor.process_query(query)
        filters = nlp_processor.extract_filters(query)
        
        return jsonify({
            'status': 'success',
            'data': {
                'nlp_analysis': nlp_result,
                'extracted_filters': filters
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@smart_shopping_bp.route('/convert-currency', methods=['POST'])
def convert_currency():
    """Convert currency"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        from_currency = data.get('from_currency', 'USD')
        to_currency = data.get('to_currency', 'USD')
        
        result = currency_converter.convert_price(amount, from_currency, to_currency)
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@smart_shopping_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'module': 'smart_shopping',
        'components': {
            'product_apis': 'active',
            'nlp_processor': 'active',
            'recommendation_engine': 'active',
            'currency_converter': 'active',
            'chat_assistant': 'active',
            'history_manager': 'active' if history_manager else 'inactive'
        }
    }), 200

