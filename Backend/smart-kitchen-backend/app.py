from flask import Flask, jsonify, request
from flask_cors import CORS
import os
<<<<<<< Updated upstream:Backend/smart-kitchen-backend/app.py
from dotenv import load_dotenv
=======
from datetime import datetime
>>>>>>> Stashed changes:Backend/app.py

load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5000", "http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

<<<<<<< Updated upstream:Backend/smart-kitchen-backend/app.py
# Import your cooking assistant module
=======
# 🔹 Import blueprints
>>>>>>> Stashed changes:Backend/app.py
from cooking_assistant.routes import cooking_bp
from shopping.routes import shopping_bp

# Register blueprints
app.register_blueprint(cooking_bp, url_prefix='/api/cooking')
app.register_blueprint(shopping_bp, url_prefix='')  # Registered at root since routes already have /api/shopping

<<<<<<< Updated upstream:Backend/smart-kitchen-backend/app.py
=======
# 🔹 Import smart shopping module
from smart_shopping.routes import smart_shopping_bp, init_history_manager
app.register_blueprint(smart_shopping_bp, url_prefix='/api/smart-shopping')

# 🔹 Initialize smart shopping history manager with MongoDB
init_history_manager(mongo_db=mongo.db)

# 🔹 Health check endpoint
>>>>>>> Stashed changes:Backend/app.py
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Smart Kitchen Backend is running!'
    }), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Welcome to Smart Kitchen API',
        'version': '1.0.0',
        'modules': {
            'cooking_assistant': {
                'endpoints': [
                    'POST /api/cooking/analyze-image',
                    'POST /api/cooking/search-recipes',
                    'POST /api/cooking/generate-grocery-list'
                ]
            },
<<<<<<< Updated upstream:Backend/smart-kitchen-backend/app.py
            'smart_shopping': {
                'endpoints': [
                    'POST /api/smart-shopping/search',
                    'POST /api/smart-shopping/recommendations',
                    'POST /api/smart-shopping/chat',
                    'GET/POST/PUT/DELETE /api/smart-shopping/history',
                    'POST /api/smart-shopping/process-query',
                    'POST /api/smart-shopping/convert-currency',
                    'GET /api/smart-shopping/health'
=======
            'shopping': {
                'endpoints': [
                    'GET /api/shopping/search?q=<query>',
                    'GET /api/shopping/product/<product_id>',
                    'GET /api/shopping/history',
                    'GET /api/shopping/recommendations'
>>>>>>> Stashed changes:Backend/app.py
                ]
            }
        }
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Smart Kitchen Backend...")
    print("📍 Backend running on: http://localhost:5000")
    print("📍 Frontend should run on: http://localhost:3000")
    app.run(debug=True, port=5000)
