from flask import Flask, jsonify, request
from flask_cors import CORS
from extensions import mongo, bcrypt, jwt
from dotenv import load_dotenv
import os
import traceback
from werkzeug.exceptions import HTTPException

# --------------------------------------------------------
# ✅ Load environment variables (Windows-safe)
# --------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)

# --------------------------------------------------------
# BASE DIR + DATA/STORE
# --------------------------------------------------------
app.config["BASE_DIR"] = BASE_DIR
app.config["DATA_DIR"] = os.path.join(app.config["BASE_DIR"], "data")
app.config["STORE_DIR"] = os.path.join(app.config["BASE_DIR"], "store")
app.config["UPLOAD_FOLDER"] = os.path.join(app.config["BASE_DIR"], "uploads")

# --------------------------------------------------------
# BASIC CONFIG
# --------------------------------------------------------
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["PROPAGATE_EXCEPTIONS"] = False  # ✅ prevents turning 404 into 500 via propagation
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")

# Ensure folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["DATA_DIR"], exist_ok=True)
os.makedirs(app.config["STORE_DIR"], exist_ok=True)

# --------------------------------------------------------
# ✅ CORS (single clean config)
# --------------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# --------------------------------------------------------
# ✅ Error handling (keep HTTP errors as-is)
# --------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    # If it's an HTTPException (404, 405, etc.), keep its status code
    if isinstance(e, HTTPException):
        return jsonify({"error": e.name, "message": e.description}), e.code

    # Otherwise, it's a real server error
    print("❌ INTERNAL ERROR:", str(e))
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# --------------------------------------------------------
# INIT EXTENSIONS
# --------------------------------------------------------
bcrypt.init_app(app)
jwt.init_app(app)

# --------------------------------------------------------
# BLUEPRINT IMPORTS
# --------------------------------------------------------
from cooking_assistant.routes import cooking_bp
from shopping.routes import shopping_bp
from auth.routes import auth_bp
from NutritionGuidance.routes import nutrition_bp

# --------------------------------------------------------
# Register blueprints
# --------------------------------------------------------
app.register_blueprint(cooking_bp, url_prefix="/api/cooking")
app.register_blueprint(shopping_bp, url_prefix="")  # shopping routes already include /api/shopping
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(nutrition_bp, url_prefix="/api/nutrition")

# --------------------------------------------------------
# ✅ FoodExpiry: enable if Mongo is configured
# --------------------------------------------------------
food_bp_available = False

MONGO_URI = os.getenv("MONGO_URI", "").strip()
if MONGO_URI:
    try:
        app.config["MONGO_URI"] = MONGO_URI
        mongo.init_app(app)

        from FoodExpiry.routes.food_routes import food_bp
        app.register_blueprint(food_bp, url_prefix="/api/food")
        food_bp_available = True
        print("✅ FoodExpiry module enabled (Mongo configured).")
    except Exception as e:
        print("⚠️ FoodExpiry disabled due to Mongo error:", str(e))
else:
    print("⚠️ FoodExpiry disabled: MONGO_URI not set. (Create Backend/.env)")

# --------------------------------------------------------
# ROUTES
# --------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Smart Kitchen Backend is running!"}), 200

@app.route("/", methods=["GET"])
def root():
    modules = {
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
            ]
        }
    }

    if food_bp_available:
        modules["food_expiry_predictor"] = {
            "endpoints": [
                "GET /api/food/",
                "POST /api/food/add",
                "POST /api/food/predict",
                "PUT /api/food/update/<id>",
                "POST /api/food/feedback",
                "DELETE /api/food/delete/<id>",
            ]
        }

    return jsonify({"message": "Welcome to Smart Kitchen API", "version": "1.0.0", "modules": modules}), 200

# --------------------------------------------------------
# RUN
# --------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Smart Kitchen Backend...")
    print("📍 Backend running on: http://127.0.0.1:5000")
    print("📍 Frontend: http://localhost:5173")
    # ✅ Avoid Windows socket reloader glitch
    app.run(debug=True, port=5000, use_reloader=False)
