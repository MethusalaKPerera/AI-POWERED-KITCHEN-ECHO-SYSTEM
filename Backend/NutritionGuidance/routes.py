
from flask import Blueprint, current_app, request

from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.food_search import search_foods
from NutritionGuidance.services.profile_store import get_profile, save_profile


# -------------------------------------------------
# Blueprint
# -------------------------------------------------
nutrition_bp = Blueprint("nutrition_bp", __name__)


# -------------------------------------------------
# STEP 1: Dataset status (verification)
# -------------------------------------------------
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


# -------------------------------------------------
# STEP 2: Food search (autocomplete)
# -------------------------------------------------
@nutrition_bp.route("/foods/search", methods=["GET"])
def foods_search():
    q = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit") or 15)

    food_df, _, _ = get_datasets(current_app)
    return {
        "items": search_foods(food_df, q, limit=limit)
    }


# -------------------------------------------------
# STEP 3: User profile (GET + POST)
# -------------------------------------------------

# GET profile (accepts /profile and /profile/)
@nutrition_bp.route("/profile", methods=["GET"])
@nutrition_bp.route("/profile/", methods=["GET"])
def profile_get():
    user_id = (request.args.get("user_id") or "demo").strip()
    profile = get_profile(current_app, user_id)
    return {"profile": profile}


# POST profile (accepts /profile and /profile/)
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

    return {
        "message": "Profile saved successfully",
        "profile": saved_profile
    }
