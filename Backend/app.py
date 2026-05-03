from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from extensions import mongo, bcrypt, jwt
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
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
app.config["DATA_DIR"] = os.path.join(app.config["BASE_DIR"], "data")
app.config["STORE_DIR"] = os.path.join(app.config["BASE_DIR"], "store")
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
# CORS
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

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
    else:
        resp.headers["Access-Control-Allow-Origin"] = origin or "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp

# --------------------------------------------------------
# Error handler
# --------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.name, "message": e.description}), e.code
    print("ERROR:", str(e))
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# --------------------------------------------------------
# Init extensions (Mongo optional)
# --------------------------------------------------------
bcrypt.init_app(app)
jwt.init_app(app)

# --------------------------------------------------------
# Import & register blueprints
# --------------------------------------------------------
from cooking_assistant.routes import cooking_bp
from shopping.routes import shopping_bp
from auth.routes import auth_bp
from NutritionGuidance.routes import nutrition_bp

app.register_blueprint(cooking_bp, url_prefix="/api/cooking")
app.register_blueprint(shopping_bp, url_prefix="")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(nutrition_bp, url_prefix="/api/nutrition")

# --------------------------------------------------------
# FoodExpiry (only if Mongo configured)
# --------------------------------------------------------
food_bp_available = False
food_disabled_reason = None
try:
    MONGO_URI = os.getenv("MONGO_URI", "").strip()
    if MONGO_URI:
        app.config["MONGO_URI"] = MONGO_URI
        mongo.init_app(app)
        from FoodExpiry.routes.food_routes import food_bp
        app.register_blueprint(food_bp, url_prefix="/api/food")
        food_bp_available = True
        print("[OK] FoodExpiry enabled (Mongo connected).")
    else:
        food_disabled_reason = "MONGO_URI is not set"
        print("[WARN] FoodExpiry disabled (MONGO_URI not set).")
except Exception as e:
    if isinstance(e, ModuleNotFoundError) and "catboost" in str(e):
        food_disabled_reason = "missing dependency: catboost"
        print("[WARN] FoodExpiry disabled due to missing dependency: catboost is required.")
        print("       Install it with: python -m pip install -r Backend/requirements.txt")
    else:
        food_disabled_reason = f"Mongo error: {str(e)}"
        print("[WARN] FoodExpiry disabled due to Mongo error:", str(e))
    food_bp_available = False

if not food_bp_available:
    disabled_bp = Blueprint("food_disabled_bp", __name__)
    unavailable_msg = (
        f"FoodExpiry module is disabled: {food_disabled_reason}. "
        "Please check MONGO_URI, install missing dependencies, and restart the backend."
    )

    @disabled_bp.route("/", methods=["GET"])
    def food_index():
        return jsonify([]), 200

    @disabled_bp.route("/options", methods=["GET"])
    def food_options():
        categories = [
            "dairy", "meat", "fish", "fruit", "vegetable",
            "grain", "snack", "beverage", "other"
        ]
        return jsonify({"items": [], "categories": categories}), 200

    @disabled_bp.route("/analytics/summary", methods=["GET"])
    def analytics_summary():
        return jsonify({"summary": {}, "message": unavailable_msg}), 200

    @disabled_bp.route("/analytics/timeseries", methods=["GET"])
    def analytics_timeseries():
        return jsonify({"series": [], "message": unavailable_msg}), 200

    @disabled_bp.route("/analytics/history", methods=["GET"])
    def analytics_history():
        return jsonify({"rows": [], "total": 0, "message": unavailable_msg}), 200

    @disabled_bp.route("/analytics/export/csv", methods=["GET"])
    @disabled_bp.route("/analytics/export/pdf", methods=["GET"])
    def analytics_export():
        return jsonify({"error": "FoodExpiry unavailable", "message": unavailable_msg}), 200

    @disabled_bp.route("/one/<id>", methods=["GET"])
    def food_one(id):
        return jsonify({"error": "FoodExpiry unavailable", "message": unavailable_msg}), 200

    @disabled_bp.route("/predict", methods=["POST"])
    @disabled_bp.route("/add", methods=["POST"])
    @disabled_bp.route("/feedback", methods=["POST"])
    @disabled_bp.route("/update/<id>", methods=["PUT"])
    @disabled_bp.route("/delete/<id>", methods=["DELETE"])
    def food_unavailable(**kwargs):
        return jsonify({"error": "FoodExpiry unavailable", "message": unavailable_msg}), 200

    app.register_blueprint(disabled_bp, url_prefix="/api/food")

# --------------------------------------------------------
# Health check
# --------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    modules_status = {
        "cooking_assistant": {"enabled": True, "reason": "always available"},
        "shopping": {"enabled": True, "reason": "always available"},
        "auth": {"enabled": True, "reason": "always available"},
        "nutrition_guidance": {"enabled": True, "reason": "always available"},
        "food_expiry": {
            "enabled": food_bp_available,
            "reason": food_disabled_reason if not food_bp_available else "MongoDB connected and dependencies available"
        }
    }
    
    overall_status = "healthy" if all(m["enabled"] for m in modules_status.values()) else "degraded"
    
    return jsonify({
        "status": overall_status,
        "message": "Smart Kitchen Backend is running!",
        "modules": modules_status
    }), 200

# --------------------------------------------------------
# Root route
# --------------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    modules = {
        "cooking_assistant": {
            "endpoints": [
                "POST /api/cooking/analyze-image",
                "POST /api/cooking/search-recipes",
                "GET  /api/cooking/sbert-status",
                "POST /api/cooking/grocery-from-meals",
                "POST /api/cooking/parse-meal-plan",
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
                "POST /api/nutrition/profile",
                "POST /api/nutrition/intake/add",
                "GET /api/nutrition/report?period=weekly|monthly",
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

    return jsonify({
        "message": "Welcome to Smart Kitchen API",
        "version": "1.0.0",
        "modules": modules
    }), 200

# --------------------------------------------------------
# Run
# --------------------------------------------------------
if __name__ == "__main__":
    print("Starting Smart Kitchen Backend...")
    print("Backend running on: http://127.0.0.1:5000")
    print("Frontend should run on: http://localhost:5173")
    app.run(debug=True, port=5000)
