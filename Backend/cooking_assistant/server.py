"""
AI-Powered Kitchen Echo System - Complete Server
Integrates all route blueprints including meal planner
"""
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(__name__)

# Enable CORS for frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Import and register blueprints
blueprints_loaded = []

try:
    from enhanced_routes import enhanced_bp
    app.register_blueprint(enhanced_bp, url_prefix='/api')
    blueprints_loaded.append("enhanced_routes")
    print("✓ Loaded enhanced_routes (enhanced_bp)")
except ImportError as e:
    print(f"⚠ Could not load enhanced_routes: {e}")

try:
    from routes import cooking_bp
    app.register_blueprint(cooking_bp, url_prefix='/api')
    blueprints_loaded.append("routes")
    print("✓ Loaded routes (cooking_bp)")
except ImportError as e:
    print(f"⚠ Could not load routes: {e}")

try:
    from meal_planner_routes import meal_planner_bp
    app.register_blueprint(meal_planner_bp, url_prefix='/api')
    blueprints_loaded.append("meal_planner")
    print("✓ Loaded meal_planner_routes (meal_planner_bp)")
except ImportError as e:
    print(f"⚠ Could not load meal_planner_routes: {e}")

# Root endpoint
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "AI-Powered Kitchen Echo System API",
        "version": "2.0.0",
        "features": [
            "🍛 Recipe Suggestions with ML",
            "📷 Computer Vision (Image Recognition)",
            "📅 AI Meal Planning",
            "🛒 Smart Grocery Lists",
            "🌍 Multi-language Support (EN/SI/TA)"
        ],
        "endpoints": {
            "health": "/health",
            "system_stats": "/api/system-stats",
            "search_recipes": "/api/search-recipes-enhanced",
            "analyze_image": "/api/analyze-image-enhanced",
            "meal_plan": "/api/generate-meal-plan",
            "grocery_list": "/api/generate-grocery-list"
        },
        "blueprints_loaded": blueprints_loaded
    })

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "cooking-assistant",
        "blueprints_loaded": len(app.blueprints),
        "active_blueprints": blueprints_loaded
    })

if __name__ == "__main__":
    print("=" * 70)
    print("🍳 AI-POWERED KITCHEN ECHO SYSTEM - Backend Server v2.0")
    print("=" * 70)
    print(f"Server starting on http://localhost:5000")
    print(f"Frontend should be on http://localhost:5173")
    print(f"Blueprints loaded: {len(blueprints_loaded)} - {', '.join(blueprints_loaded)}")
    print("=" * 70)
    app.run(host="0.0.0.0", port=5000, debug=True)