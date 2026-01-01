from flask import Blueprint, current_app, request
from NutritionGuidance.services.profile_store import get_profile, save_profile
from NutritionGuidance.services.food_search import search_foods
from NutritionGuidance.services.intake_store import add_intake, get_summary
from NutritionGuidance.services.report_service import build_report
from NutritionGuidance.services.dataset_loader import get_datasets

nutrition_bp = Blueprint("nutrition_bp", __name__)

# ✅ Health ping
@nutrition_bp.route("/health", methods=["GET", "OPTIONS"])
def nutrition_health():
    if request.method == "OPTIONS":
        return ("", 200)
    return {"status": "ok", "module": "NutritionGuidance"}

# ✅ Conditions list
@nutrition_bp.route("/conditions", methods=["GET", "OPTIONS"])
def conditions_list():
    if request.method == "OPTIONS":
        return ("", 200)

    _, _, cond_df = get_datasets(current_app)
    if cond_df is None or cond_df.empty:
        return {"items": []}

    col = "condition" if "condition" in cond_df.columns else cond_df.columns[0]
    items = sorted({str(x).strip() for x in cond_df[col].dropna().tolist() if str(x).strip()})
    return {"items": [{"condition": x} for x in items]}

# ✅ GET profile
@nutrition_bp.route("/profile", methods=["GET", "OPTIONS"])
@nutrition_bp.route("/profile/", methods=["GET", "OPTIONS"])
def profile_get():
    if request.method == "OPTIONS":
        return ("", 200)
    user_id = (request.args.get("user_id") or "demo").strip()
    return {"profile": get_profile(current_app, user_id)}

# ✅ POST profile
@nutrition_bp.route("/profile", methods=["POST", "OPTIONS"])
@nutrition_bp.route("/profile/", methods=["POST", "OPTIONS"])
def profile_post():
    if request.method == "OPTIONS":
        return ("", 200)

    payload = request.get_json(force=True) or {}
    user_id = (payload.get("user_id") or "demo").strip()

    profile = {
        "age": payload.get("age"),
        "group": payload.get("group"),
        "conditions": payload.get("conditions") or [],
    }

    saved = save_profile(current_app, user_id, profile)
    return {"message": "Profile saved successfully", "profile": saved}

# ✅ Food search
@nutrition_bp.route("/foods/search", methods=["GET", "OPTIONS"])
def foods_search():
    if request.method == "OPTIONS":
        return ("", 200)
    q = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit") or 15)
    food_df, _, _ = get_datasets(current_app)
    items = search_foods(food_df, q, limit=limit)
    return {"items": items}

# ✅ Add intake
@nutrition_bp.route("/intake/add", methods=["POST", "OPTIONS"])
def intake_add():
    if request.method == "OPTIONS":
        return ("", 200)

    payload = request.get_json(force=True) or {}
    user_id = (payload.get("user_id") or "demo").strip()
    food_id = (payload.get("food_id") or "").strip()
    food_name = (payload.get("food_name") or "").strip()
    quantity = payload.get("quantity") or 1
    date_str = (payload.get("date") or "").strip()

    saved = add_intake(current_app, user_id, food_id, food_name, quantity, date_str)
    return {"message": "Intake saved", "item": saved}

# ✅ Summary
@nutrition_bp.route("/intake/summary", methods=["GET", "OPTIONS"])
def intake_summary():
    if request.method == "OPTIONS":
        return ("", 200)
    user_id = (request.args.get("user_id") or "demo").strip()
    period = (request.args.get("period") or "weekly").strip()
    return get_summary(current_app, user_id, period)

# ✅ Report
@nutrition_bp.route("/report", methods=["GET", "OPTIONS"])
def report():
    if request.method == "OPTIONS":
        return ("", 200)
    user_id = (request.args.get("user_id") or "demo").strip()
    period = (request.args.get("period") or "monthly").strip()
    return build_report(current_app, user_id, period)
