from flask import Blueprint, current_app, request
from NutritionGuidance.services.dataset_loader import get_datasets

# ✅ THIS is the object your app.py is trying to import
nutrition_bp = Blueprint("nutrition_bp", __name__)

@nutrition_bp.get("/datasets/status")
def datasets_status():
    food_df, req_df, cond_df = get_datasets(current_app)

    return {
        "status": "ok",
        "data_dir": current_app.config.get("DATA_DIR"),
        "shapes": {
            "food": [int(food_df.shape[0]), int(food_df.shape[1])],
            "requirements": [int(req_df.shape[0]), int(req_df.shape[1])],
            "conditions": [int(cond_df.shape[0]), int(cond_df.shape[1])],
        },
        "sample_food_names": food_df["food_name"].head(10).tolist(),
        "sample_food_columns": list(food_df.columns)[:15],
    }

@nutrition_bp.get("/foods/search")
def foods_search():
    q = (request.args.get("q") or "").strip().lower()
    limit = int(request.args.get("limit") or 15)

    food_df, _, _ = get_datasets(current_app)

    if not q:
        return {"items": []}

    m = food_df["food_name"].astype(str).str.lower().str.contains(q, na=False)
    cols = ["food_name"]

    # include food_id if exists
    if "food_id" in food_df.columns:
        cols = ["food_id"] + cols

    # include serving columns if exist
    for c in ["serving_basis", "serving_size_g"]:
        if c in food_df.columns and c not in cols:
            cols.append(c)

    out = food_df.loc[m, cols].head(limit)
    return {"items": out.to_dict(orient="records")}
