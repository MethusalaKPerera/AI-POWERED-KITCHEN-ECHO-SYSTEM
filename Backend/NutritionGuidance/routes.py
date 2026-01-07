
from flask import Blueprint, current_app, request

# IMPORT SERVICES ONLY (NO ROUTE IMPORTS)
from NutritionGuidance.services.profile_store import get_profile, save_profile
from NutritionGuidance.services.food_search import search_foods
from NutritionGuidance.services.intake_store import add_intake, get_summary
from NutritionGuidance.services.report_service import build_report
from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.ml_risk_service import predict_risk

# trained 2-week report (4 nutrients only)
from NutritionGuidance.services.trained_report_service import build_trained_two_week_report

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

    # accept optional "ts" so old-date logs can keep consistent timestamps
    item = add_intake(
        current_app,
        data.get("user_id", "demo"),
        data.get("food_id"),
        data.get("food_name"),
        data.get("quantity", 1),
        data.get("date"),
        data.get("ts"),  
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
# REPORT (full report with many nutrients)
# --------------------------------------------------
@nutrition_bp.route("/report", methods=["GET"])
def report():
    return build_report(
        current_app,
        request.args.get("user_id", "demo"),
        request.args.get("period", "monthly"),
    )

# --------------------------------------------------
# TRAINED 4-NUTRIENTS NEXT 2 WEEKS REPORT
# --------------------------------------------------
@nutrition_bp.route("/report/trained", methods=["GET"])
def trained_report():
    user_id = request.args.get("user_id", "demo")
    period = request.args.get("period", "monthly")
    try:
        days = int(request.args.get("days", 14))
    except Exception:
        days = 14

    days = max(1, min(days, 60))  # safety clamp

    return build_trained_two_week_report(current_app, user_id, period, days)

# --------------------------------------------------
# ML DEFICIENCY RISK
# --------------------------------------------------
@nutrition_bp.route("/ml-risk", methods=["GET"])
def ml_risk():
    user_id = request.args.get("user_id", "demo")
    period = request.args.get("period", "monthly")

    profile = get_profile(current_app, user_id) or {}

    # Safe age parsing
    try:
        age = int(profile.get("age") or 22)
    except Exception:
        age = 22

    # Summary + avg fallback
    summary = get_summary(current_app, user_id, period) or {}
    # Keep both keys compatibility
    avg = summary.get("daily_average_over_period") or summary.get("daily_average") or summary.get("daily_average_logged_days") or {}

    # Condition: pick first (you can enhance later to support multiple)
    conditions = profile.get("conditions") or []
    condition = conditions[0] if isinstance(conditions, list) and len(conditions) > 0 else None

    risk = predict_risk(age, avg, condition=condition)

    return {
        "user_id": user_id,
        "period": period,
        "ml_deficiency_risk": risk,
        "age": age,
        "condition": condition,
        "inputs_used": {
            "energy_kcal": float(avg.get("energy_kcal", 0) or 0),
            "protein_g": float(avg.get("protein_g", 0) or 0),
            "calcium_mg": float(avg.get("calcium_mg", 0) or 0),
            "iron_mg": float(avg.get("iron_mg", 0) or 0),
        },
    }
