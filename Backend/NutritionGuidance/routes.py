
from flask import Blueprint, current_app, request

from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.food_search import search_foods
from NutritionGuidance.services.profile_store import get_profile, save_profile
from NutritionGuidance.services.intake_store import add_intake, get_summary

from NutritionGuidance.services.intake_store import get_summary
from NutritionGuidance.services.recommendations import recommend_foods_for_gaps
from NutritionGuidance.services.report_service import build_report

nutrition_bp = Blueprint("nutrition_bp", __name__)


# ---------------------------
# STEP 1: Dataset status
# ---------------------------
@nutrition_bp.route("/datasets/status", methods=["GET"])
def datasets_status():
    food_df, req_df, cond_df = get_datasets(current_app)

    return {
        "status": "ok",
        "data_dir": current_app.config.get("DATA_DIR"),
        "shapes": {
            "food": [int(food_df.shape[0]), int(food_df.shape[1])],
            "requirements": [int(req_df.shape[0]), int(req_df.shape[1])],
            "conditions": [int(cond_df.shape[0]), int(cond_df.shape[1])]
        },
        "sample_food_columns": list(food_df.columns)[:15],
        "sample_food_names": food_df["food_name"].head(10).tolist(),
    }


# ---------------------------
# STEP 2: Food search
# ---------------------------
@nutrition_bp.route("/foods/search", methods=["GET"])
def foods_search():
    q = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit") or 15)

    food_df, _, _ = get_datasets(current_app)
    return {"items": search_foods(food_df, q, limit=limit)}


# ---------------------------
# STEP 3: Profile (GET + POST)
# ---------------------------
@nutrition_bp.route("/profile", methods=["GET"])
@nutrition_bp.route("/profile/", methods=["GET"])
def profile_get():
    user_id = (request.args.get("user_id") or "demo").strip()
    profile = get_profile(current_app, user_id)
    return {"profile": profile}


@nutrition_bp.route("/profile", methods=["POST"])
@nutrition_bp.route("/profile/", methods=["POST"])
def profile_post():
    payload = request.get_json(force=True) or {}
    user_id = (payload.get("user_id") or "demo").strip()

    profile_data = {
        "age": payload.get("age"),
        "group": payload.get("group"),
        "conditions": payload.get("conditions"),
    }

    saved_profile = save_profile(current_app, user_id, profile_data)
    return {"message": "Profile saved successfully", "profile": saved_profile}


# ---------------------------
# STEP 4: Intake logging
# ---------------------------
@nutrition_bp.route("/intake/add", methods=["POST"])
@nutrition_bp.route("/intake/add/", methods=["POST"])
def intake_add():
    payload = request.get_json(force=True) or {}

    user_id = (payload.get("user_id") or "demo").strip()
    food_id = (payload.get("food_id") or "").strip()
    food_name = (payload.get("food_name") or "").strip()
    quantity = payload.get("quantity", 1.0)
    date = (payload.get("date") or "").strip()  # YYYY-MM-DD required

    if not date:
        return {"error": "date is required (YYYY-MM-DD)"}, 400

    try:
        rec = add_intake(current_app, user_id, food_id, food_name, quantity, date)
        return {"message": "Intake added", "record": rec}
    except Exception as e:
        return {"error": str(e)}, 400


@nutrition_bp.route("/intake/summary", methods=["GET"])
@nutrition_bp.route("/intake/summary/", methods=["GET"])
def intake_summary():
    user_id = (request.args.get("user_id") or "demo").strip()
    period = (request.args.get("period") or "weekly").strip().lower()  # weekly/monthly
    return get_summary(current_app, user_id, period)


@nutrition_bp.route("/report", methods=["GET"])
@nutrition_bp.route("/report/", methods=["GET"])
def nutrition_report():
    user_id = (request.args.get("user_id") or "demo").strip()
    period = (request.args.get("period") or "monthly").strip().lower()

    food_df, req_df, cond_df = get_datasets(current_app)
    profile = get_profile(current_app, user_id)
    summary = get_summary(current_app, user_id, period)

    report = build_report(req_df, cond_df, profile, summary)
    report["recommendations"] = recommend_foods_for_gaps(food_df, report.get("gaps", {}), top_k=8)

    report["user_id"] = user_id
    report["period"] = period
    return report
