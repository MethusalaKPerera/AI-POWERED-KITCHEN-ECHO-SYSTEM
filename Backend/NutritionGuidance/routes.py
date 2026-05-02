
from flask import Blueprint, current_app, request

# IMPORT SERVICES ONLY (NO ROUTE IMPORTS)
from NutritionGuidance.services.profile_store import get_profile, save_profile
from NutritionGuidance.services.food_search import search_foods
from NutritionGuidance.services.intake_store import add_intake, get_summary
from NutritionGuidance.services.report_service import build_report
from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.ml_deficiency_predictor import predict_deficiency_risk
from NutritionGuidance.services.requirement_service import pick_requirements

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

    try:
        age = int(profile.get("age") or 22)
    except Exception:
        age = 22

    group = profile.get("group") or "general"
    conditions = profile.get("conditions") or []
    condition = conditions[0] if isinstance(conditions, list) and len(conditions) > 0 else None

    summary = get_summary(current_app, user_id, period) or {}
    avg = (
        summary.get("daily_average_over_period")
        or summary.get("daily_average")
        or summary.get("daily_average_logged_days")
        or {}
    )

    _, req_df, _ = get_datasets(current_app)
    requirement = pick_requirements(req_df, age, group) or {}

    condition_flag = 1 if condition else 0

    gender_code = 2
    if str(group).lower().startswith("m"):
        gender_code = 1
    elif str(group).lower().startswith("f"):
        gender_code = 0

    user_features = {
        "age": age,
        "gender_code": gender_code,
        "condition_flag": condition_flag,

        "energy_intake": float(avg.get("energy_kcal", 0) or 0),
        "protein_intake": float(avg.get("protein_g", 0) or 0),
        "calcium_intake": float(avg.get("calcium_mg", 0) or 0),
        "iron_intake": float(avg.get("iron_mg", 0) or 0),

        "required_energy": float(requirement.get("energy_kcal", 0) or requirement.get("energy", 0) or 0),
        "required_protein": float(requirement.get("protein_g", 0) or requirement.get("protein", 0) or 0),
        "required_calcium": float(requirement.get("calcium_mg", 0) or requirement.get("calcium", 0) or 0),
        "required_iron": float(requirement.get("iron_mg", 0) or requirement.get("iron", 0) or 0),
    }

    risk = predict_deficiency_risk(user_features)

    return {
        "user_id": user_id,
        "period": period,
        "ml_deficiency_risk": risk,
        "age": age,
        "group": group,
        "condition": condition,
        "inputs_used": user_features,
    }

# --------------------------------------------------
# ML DEFICIENCY RISK SIMULATION (Custom inputs)
# --------------------------------------------------
@nutrition_bp.route("/ml-risk/simulate", methods=["POST"])
def ml_risk_simulate():
    data = request.get_json(force=True) or {}

    try:
        age = int(data.get("age", 30))
    except Exception:
        age = 30

    condition = data.get("condition")
    condition_flag = 1 if condition else 0

    user_features = {
        "age": age,
        "gender_code": int(data.get("gender_code", 2)),
        "condition_flag": condition_flag,

        "energy_intake": float(data.get("energy_kcal", 0) or 0),
        "protein_intake": float(data.get("protein_g", 0) or 0),
        "calcium_intake": float(data.get("calcium_mg", 0) or 0),
        "iron_intake": float(data.get("iron_mg", 0) or 0),

        "required_energy": float(data.get("required_energy", 2200) or 2200),
        "required_protein": float(data.get("required_protein", 55) or 55),
        "required_calcium": float(data.get("required_calcium", 1000) or 1000),
        "required_iron": float(data.get("required_iron", 18) or 18),
    }

    risk = predict_deficiency_risk(user_features)

    return {
        "ml_deficiency_risk": risk,
        "age": age,
        "condition": condition,
        "inputs_used": user_features,
    }