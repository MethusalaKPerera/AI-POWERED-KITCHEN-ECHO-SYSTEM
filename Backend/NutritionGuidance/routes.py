from flask import Blueprint, current_app, request

# ✅ IMPORT SERVICES ONLY (NO ROUTE IMPORTS)
from NutritionGuidance.services.profile_store import get_profile, save_profile
from NutritionGuidance.services.food_search import search_foods
from NutritionGuidance.services.intake_store import add_intake, get_summary
from NutritionGuidance.services.report_service import build_report
from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.ml_risk_service import predict_risk

# --------------------------------------------------
# DEFINE BLUEPRINT ONCE
# --------------------------------------------------
nutrition_bp = Blueprint("nutrition_bp", __name__)

# --------------------------------------------------
# GLOBAL OPTIONS HANDLER (preflight safe)
# --------------------------------------------------
@nutrition_bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return ("", 200)

# --------------------------------------------------
# HEALTH
# --------------------------------------------------
@nutrition_bp.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

# --------------------------------------------------
# CONDITIONS
# --------------------------------------------------
@nutrition_bp.route("/conditions", methods=["GET"])
def conditions():
    _, _, df = get_datasets(current_app)
    if df is None or df.empty:
        return {"items": []}

    col = "condition" if "condition" in df.columns else df.columns[0]
    items = sorted(set(df[col].dropna().astype(str)))
    return {"items": [{"condition": x} for x in items]}

# --------------------------------------------------
# PROFILE
# --------------------------------------------------
@nutrition_bp.route("/profile", methods=["GET"])
def profile_get():
    user_id = request.args.get("user_id", "demo")
    return {"profile": get_profile(current_app, user_id)}

@nutrition_bp.route("/profile", methods=["POST"])
def profile_post():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id", "demo")

    profile = {
        "age": data.get("age"),
        "group": data.get("group"),
        "conditions": data.get("conditions", []),
    }

    saved = save_profile(current_app, user_id, profile)
    return {"message": "Profile saved", "profile": saved}

# --------------------------------------------------
# FOOD SEARCH
# --------------------------------------------------
@nutrition_bp.route("/foods/search", methods=["GET"])
def foods_search():
    q = request.args.get("q", "")
    food_df, _, _ = get_datasets(current_app)
    items = search_foods(food_df, q)
    return {"items": items}

# --------------------------------------------------
# INTAKE ADD
# --------------------------------------------------
@nutrition_bp.route("/intake/add", methods=["POST"])
def intake_add():
    data = request.get_json(force=True) or {}

    item = add_intake(
        current_app,
        data.get("user_id", "demo"),
        data.get("food_id"),
        data.get("food_name"),
        data.get("quantity", 1),
        data.get("date"),
    )

    return {"message": "Intake saved", "item": item}

# --------------------------------------------------
# INTAKE SUMMARY
# --------------------------------------------------
@nutrition_bp.route("/intake/summary", methods=["GET"])
def intake_summary():
    return get_summary(
        current_app,
        request.args.get("user_id", "demo"),
        request.args.get("period", "weekly"),
    )

# --------------------------------------------------
# REPORT
# --------------------------------------------------
@nutrition_bp.route("/report", methods=["GET"])
def report():
    return build_report(
        current_app,
        request.args.get("user_id", "demo"),
        request.args.get("period", "monthly"),
    )

# --------------------------------------------------
# ✅ ML DEFICIENCY RISK
# --------------------------------------------------
@nutrition_bp.route("/ml-risk", methods=["GET"])
def ml_risk():
    user_id = request.args.get("user_id", "demo")
    period = request.args.get("period", "monthly")

    profile = get_profile(current_app, user_id)
    age = int(profile.get("age", 22))

    summary = get_summary(current_app, user_id, period)
    avg = summary.get("daily_average_over_period", {})

    risk = predict_risk(age, avg)

    return {
        "user_id": user_id,
        "period": period,
        "ml_deficiency_risk": risk,
    }
