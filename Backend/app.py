from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from datetime import datetime

# 🔹 Load environment variables
load_dotenv()

# 🔹 Initialize Flask app
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

# 🔹 Basic config
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

# 🔹 MongoDB config
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# 🔹 Ensure required folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# 🔹 Import blueprints
from cooking_assistant.routes import cooking_bp
from shopping.routes import shopping_bp

# Register blueprints
app.register_blueprint(cooking_bp, url_prefix='/api/cooking')
app.register_blueprint(shopping_bp, url_prefix='')  # Registered at root since routes already have /api/shopping

# 🔹 Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Smart Kitchen Backend is running!'
    }), 200

# 🔹 Root route (overview)
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
            'shopping': {
                'endpoints': [
                    'GET /api/shopping/search?q=<query>',
                    'GET /api/shopping/product/<product_id>',
                    'GET /api/shopping/history',
                    'GET /api/shopping/recommendations'
                ]
            }
        }
    }), 200

# 🔹 MongoDB test route
@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        db_names = mongo.cx.list_database_names()
        return jsonify({
            "status": "connected",
            "databases": db_names
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# 🔹 Run the Flask app
if __name__ == '__main__':
    print("🚀 Starting Smart Kitchen Backend...")
    print("📍 Backend running on: http://localhost:5000")
    print("📍 Frontend should run on: http://localhost:3000")
    app.run(debug=True, port=5000)
