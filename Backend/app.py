from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# 🔹 Load environment variables
load_dotenv()

# 🔹 Initialize Flask app
app = Flask(__name__)
CORS(app)

# 🔹 Basic config
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

# 🔹 MongoDB config
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# 🔹 Ensure required folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# 🔹 Import cooking assistant module
from cooking_assistant.routes import cooking_bp
app.register_blueprint(cooking_bp, url_prefix='/api/cooking')

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
