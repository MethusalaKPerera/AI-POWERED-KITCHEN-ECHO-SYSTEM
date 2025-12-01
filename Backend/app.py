from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import traceback


# ------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------
# INITIALIZE FLASK APP
# ------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# ★ Show FULL error logs in terminal ★
app.config["PROPAGATE_EXCEPTIONS"] = True

# ------------------------------------------------------------
# BASIC CONFIG
# ------------------------------------------------------------
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

# ------------------------------------------------------------
# MONGODB CONNECTION
# ------------------------------------------------------------
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# ------------------------------------------------------------
# BLUEPRINT IMPORTS
# ------------------------------------------------------------

# Cooking Assistant (existing)
from cooking_assistant.routes import cooking_bp
app.register_blueprint(cooking_bp, url_prefix='/api/cooking')

# Food Expiry Predictor (your novel module)
from FoodExpiry.routes.food_routes import food_bp
app.register_blueprint(food_bp, url_prefix='/api/food')

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

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
        'modules': {
            'cooking_assistant': {
                'endpoints': [
                    'POST /api/cooking/analyze-image',
                    'POST /api/cooking/search-recipes',
                    'POST /api/cooking/generate-grocery-list'
                ]
            },
            'food_expiry_predictor': {
                'endpoints': [
                    'GET /api/food/',
                    'POST /api/food/add',
                    'POST /api/food/predict',
                    'DELETE /api/food/delete/<id>'
                ]
            }
        }
    }), 200


@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        names = mongo.cx.list_database_names()
        return jsonify({"status": "connected", "databases": names}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------------------------------------------------
# RUN SERVER
# ------------------------------------------------------------
if __name__ == '__main__':
    print("🚀 Starting Smart Kitchen Backend...")
    print("📍 Backend running on: http://localhost:5000")
    print("📍 Frontend should run on: http://localhost:3000")

    # ★ Disable reloader to avoid swallowing errors ★
    app.run(debug=True, port=5000, use_reloader=False)
