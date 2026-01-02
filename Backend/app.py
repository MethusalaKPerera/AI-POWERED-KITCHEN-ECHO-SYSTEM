from flask import Flask, jsonify, request
from flask_cors import CORS
from extensions import mongo, bcrypt, jwt
from dotenv import load_dotenv
import os
import traceback

# 🔹 Load environment variables
load_dotenv()

app = Flask(__name__)

# --------------------------------------------------------
# BASE DIR + DATA/STORE
# --------------------------------------------------------
app.config["BASE_DIR"] = os.path.dirname(os.path.abspath(__file__))
app.config["DATA_DIR"] = os.path.join(app.config["BASE_DIR"], "data")
app.config["STORE_DIR"] = os.path.join(app.config["BASE_DIR"], "store")
app.config["UPLOAD_FOLDER"] = os.path.join(app.config["BASE_DIR"], "uploads")

# --------------------------------------------------------
# BASIC CONFIG
# --------------------------------------------------------
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")

# Ensure folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["DATA_DIR"], exist_ok=True)
os.makedirs(app.config["STORE_DIR"], exist_ok=True)

# --------------------------------------------------------
# ✅ CORS (global)
# --------------------------------------------------------
CORS(
    app,
    resources={r"/*": {"origins": [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

@app.after_request
def add_global_cors_headers(resp):
    origin = request.headers.get("Origin")
    allowed = {
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    }
    resp.headers["Access-Control-Allow-Origin"] = origin if origin in allowed else "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp

# --------------------------------------------------------
# ✅ GLOBAL ERROR HANDLER
# --------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    print("❌ ERROR:", str(e))
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
# ✅ FoodExpiry: Only enable if Mongo is configured & available
# --------------------------------------------------------
food_bp_available = False

try:
    MONGO_URI = os.getenv("MONGO_URI", "").strip()
    if MONGO_URI:
        # Try to init Mongo
        app.config["MONGO_URI"] = MONGO_URI
        mongo.init_app(app)

        # Now import FoodExpiry routes safely
        from FoodExpiry.routes.food_routes import food_bp
        app.register_blueprint(food_bp, url_prefix="/api/food")
        food_bp_available = True
        print("✅ FoodExpiry module enabled (Mongo connected).")
    else:
        print("⚠️ FoodExpiry disabled: MONGO_URI not set.")
except Exception as e:
    print("⚠️ FoodExpiry disabled due to Mongo error:", str(e))
    food_bp_available = False


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
    app.run(debug=True, port=5000)
