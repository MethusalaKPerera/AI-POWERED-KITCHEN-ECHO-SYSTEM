from flask import Flask, jsonify
from flask_cors import CORS
from extensions import mongo, bcrypt, jwt
from dotenv import load_dotenv
import os
import traceback

# 🔹 Load environment variables
load_dotenv()

# 🔹 Initialize Flask app
app = Flask(__name__)

# --------------------------------------------------------
# Base directory + data/store directories
# --------------------------------------------------------
app.config["BASE_DIR"] = os.path.dirname(os.path.abspath(__file__))
app.config["DATA_DIR"] = os.path.join(app.config["BASE_DIR"], "data")    # Backend/data/
app.config["STORE_DIR"] = os.path.join(app.config["BASE_DIR"], "store")  # Backend/store/

# --------------------------------------------------------
# CORS
# --------------------------------------------------------
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5000",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# --------------------------------------------------------
# Basic config
# --------------------------------------------------------
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join(app.config["BASE_DIR"], "uploads")
app.config["PROPAGATE_EXCEPTIONS"] = True

# --------------------------------------------------------
# ✅ MongoDB & Auth config
# --------------------------------------------------------
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/SmartKitchen")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")

# init extensions
mongo.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

# --------------------------------------------------------
# Ensure required folders exist
# --------------------------------------------------------
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["DATA_DIR"], exist_ok=True)
os.makedirs(app.config["STORE_DIR"], exist_ok=True)

# (Optional compatibility: if any older code expects relative "./data")
os.makedirs("data", exist_ok=True)

# --------------------------------------------------------
# Import blueprints
# --------------------------------------------------------
from cooking_assistant.routes import cooking_bp
from shopping.routes import shopping_bp
from auth.routes import auth_bp
from NutritionGuidance.routes import nutrition_bp

# Food Expiry Predictor (safe import)
food_bp_available = False
food_bp_error = None
try:
    from FoodExpiry.routes.food_routes import food_bp
    food_bp_available = True
except Exception as e:
    food_bp_available = False
    food_bp_error = str(e)
    print("⚠ FoodExpiry blueprint not available:", food_bp_error)
    traceback.print_exc()

# --------------------------------------------------------
# Register blueprints
# --------------------------------------------------------
app.register_blueprint(cooking_bp, url_prefix="/api/cooking")
app.register_blueprint(shopping_bp, url_prefix="")  # routes already include /api/shopping
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(nutrition_bp, url_prefix="/api/nutrition")

# FoodExpiry endpoints will be under /api/food/*
if food_bp_available:
    app.register_blueprint(food_bp, url_prefix="/api/food")

# --------------------------------------------------------
# Health check
# --------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Smart Kitchen Backend is running!",
        "mongo_uri_loaded": bool(os.getenv("MONGO_URI")),
        "food_expiry_enabled": food_bp_available,
        "food_expiry_error": food_bp_error
    }), 200

# --------------------------------------------------------
# Root overview
# --------------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    modules = {
        "cooking_assistant": {
            "endpoints": [
                "POST /api/cooking/analyze-image",
                "POST /api/cooking/search-recipes",
                "POST /api/cooking/generate-grocery-list"
            ]
        },
        "shopping": {
            "endpoints": [
                "GET /api/shopping/search?q=<query>",
                "GET /api/shopping/product/<product_id>",
                "GET /api/shopping/history",
                "GET /api/shopping/recommendations"
            ]
        },
        "auth": {
            "endpoints": [
                "POST /api/auth/register",
                "POST /api/auth/login"
            ]
        },
        "nutrition_guidance": {
            "endpoints": [
                "GET /api/nutrition/datasets/status",
                "GET /api/nutrition/foods/search?q=<query>",
                "GET /api/nutrition/profile?user_id=<id>",
                "POST /api/nutrition/profile",
                "POST /api/nutrition/intake/add",
                "GET /api/nutrition/intake/summary?user_id=<id>&period=weekly|monthly",
                "GET /api/nutrition/report?user_id=<id>&period=weekly|monthly"
            ]
        }
    }

    if food_bp_available:
        modules["food_expiry_predictor"] = {
            "endpoints": [
                "GET /api/food/",
                "POST /api/food/add",
                "POST /api/food/predict",
                "POST /api/food/feedback",
                "PUT /api/food/update/<id>",
                "DELETE /api/food/delete/<id>"
            ]
        }

    return jsonify({
        "message": "Welcome to Smart Kitchen API",
        "version": "1.0.0",
        "modules": modules
    }), 200

# --------------------------------------------------------
# MongoDB test route
# --------------------------------------------------------
@app.route("/test-db", methods=["GET"])
def test_db():
    try:
        db_names = mongo.cx.list_database_names()
        return jsonify({"status": "connected", "databases": db_names}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --------------------------------------------------------
# Run the Flask app
# --------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Smart Kitchen Backend...")
    print("📍 Backend running on: http://localhost:5000")
    print("📍 Frontend should run on: http://localhost:5173 or http://localhost:3000")
    print("📍 DATA_DIR:", app.config["DATA_DIR"])
    print("📍 STORE_DIR:", app.config["STORE_DIR"])
    if food_bp_available:
        print("📍 Food Expiry API: http://localhost:5000/api/food/")
    else:
        print("⚠ Food Expiry API disabled:", food_bp_error)

    app.run(debug=True, port=5000)
