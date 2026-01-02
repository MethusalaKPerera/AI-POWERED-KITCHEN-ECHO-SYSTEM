from flask import Flask, jsonify, request
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
# BASE DIR + data/store directories
# --------------------------------------------------------
app.config["BASE_DIR"] = os.path.dirname(os.path.abspath(__file__))
app.config["DATA_DIR"] = os.path.join(app.config["BASE_DIR"], "data")     # backend/data/
app.config["STORE_DIR"] = os.path.join(app.config["BASE_DIR"], "store")   # backend/store/
app.config["UPLOAD_FOLDER"] = os.path.join(app.config["BASE_DIR"], "uploads")

# --------------------------------------------------------
# Basic config
# --------------------------------------------------------
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret")

# Ensure required folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["DATA_DIR"], exist_ok=True)
os.makedirs(app.config["STORE_DIR"], exist_ok=True)

# --------------------------------------------------------
# ✅ CORS (keep origins list like your original)
# --------------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# ✅ Force CORS headers on every response (even errors)
@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
    else:
        # Keep as '*' ONLY if you want, but safer to reflect allowed origins
        resp.headers["Access-Control-Allow-Origin"] = origin or "*"

    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp

# --------------------------------------------------------
# ✅ Error handler (helps you see real error instead of CORS hiding it)
# --------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    print("❌ ERROR:", str(e))
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# --------------------------------------------------------
# Init extensions (Mongo optional)
# --------------------------------------------------------
bcrypt.init_app(app)
jwt.init_app(app)

# --------------------------------------------------------
# Import blueprints (teammates modules)
# --------------------------------------------------------
from cooking_assistant.routes import cooking_bp
from shopping.routes import shopping_bp
from auth.routes import auth_bp
from NutritionGuidance.routes import nutrition_bp

# Register blueprints (keep your previous routing)
app.register_blueprint(cooking_bp, url_prefix="/api/cooking")
app.register_blueprint(shopping_bp, url_prefix="")  # if routes already include /api/shopping
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(nutrition_bp, url_prefix="/api/nutrition")

# --------------------------------------------------------
# ✅ FoodExpiry (ONLY enable if Mongo configured)
# --------------------------------------------------------
food_bp_available = False
try:
    MONGO_URI = os.getenv("MONGO_URI", "").strip()
    if MONGO_URI:
        app.config["MONGO_URI"] = MONGO_URI
        mongo.init_app(app)

        from FoodExpiry.routes.food_routes import food_bp
        app.register_blueprint(food_bp, url_prefix="/api/food")
        food_bp_available = True
        print("✅ FoodExpiry enabled (Mongo connected).")
    else:
        print("⚠️ FoodExpiry disabled (MONGO_URI not set).")
except Exception as e:
    print("⚠️ FoodExpiry disabled due to Mongo error:", str(e))
    food_bp_available = False

# --------------------------------------------------------
# Health check endpoint
# --------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Smart Kitchen Backend is running!"}), 200

# --------------------------------------------------------
# Root route (overview)
# --------------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    modules = {
        "cooking_assistant": {
            "endpoints": [
                "POST /api/cooking/analyze-image",
                "POST /api/cooking/search-recipes",
                "POST /api/cooking/generate-grocery-list",
            ]
        },
        "shopping": {
            "endpoints": [
                "GET /api/shopping/search?q=<query>",
                "GET /api/shopping/product/<product_id>",
                "GET /api/shopping/history",
                "GET /api/shopping/recommendations",
            ]
        },
        "nutrition_guidance": {
            "endpoints": [
                "GET /api/nutrition/health",
                "GET /api/nutrition/foods/search?q=<q>",
                "GET /api/nutrition/conditions",
                "GET /api/nutrition/profile?user_id=<id>",
                "POST /api/nutrition/profile",
                "POST /api/nutrition/intake/add",
                "GET /api/nutrition/intake/summary?period=weekly|monthly",
                "GET /api/nutrition/report?period=weekly|monthly",
                "GET /api/nutrition/ml-risk?period=weekly|monthly",
            ]
        },
    }

    if food_bp_available:
        modules["food_expiry_predictor"] = {
            "endpoints": [
                "GET /api/food/",
                "POST /api/food/add",
                "POST /api/food/predict",
                "DELETE /api/food/delete/<id>",
            ]
        }

    return jsonify({"message": "Welcome to Smart Kitchen API", "version": "1.0.0", "modules": modules}), 200

# --------------------------------------------------------
# Run the Flask app
# --------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Smart Kitchen Backend...")
    print("📍 Backend running on: http://127.0.0.1:5000")
    print("📍 Frontend should run on: http://localhost:5173")
    app.run(debug=True, port=5000)
