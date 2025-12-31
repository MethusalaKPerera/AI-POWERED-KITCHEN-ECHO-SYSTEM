from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime, timedelta
import traceback

from FoodExpiry.database.db_connection import foods_col, users_col
from FoodExpiry.models.expiry_predictor import ExpiryPredictor
from FoodExpiry.ml.aed_adjuster import apply_aed, update_aed_single
from FoodExpiry.ml.scp_ranker import scp_score

food_bp = Blueprint("food_bp", __name__)
predictor = ExpiryPredictor()


def compute_expiry_date(purchase_date_str: str, days: float):
    try:
        dt = datetime.strptime(purchase_date_str, "%Y-%m-%d")
        return (dt + timedelta(days=max(0, int(days)))).strftime("%Y-%m-%d")
    except:
        return None


# ----------------------------------------------------
# GET ALL FOODS
# ----------------------------------------------------
@food_bp.route("/", methods=["GET"])
def get_foods():
    foods = list(foods_col.find())
    for f in foods:
        f["_id"] = str(f["_id"])
    return jsonify(foods), 200


# ----------------------------------------------------
# PREDICT ONLY
# ----------------------------------------------------
@food_bp.route("/predict", methods=["POST"])
def predict_only():
    try:
        data = request.get_json() or {}
        print("📩 /predict received:", data)

        user_id = data.get("userId")
        category = data.get("item_category")
        purchase_date = data.get("purchase_date")
        item_name = (data.get("item_name") or "").lower().strip()

        if not user_id or not category:
            return jsonify({"error": "Missing required fields"}), 400

        # Validate item (must exist in trained one-hot: food_<item>)
        if not predictor.validate_item(item_name):
            return jsonify({
                "error": f"Unknown item_name '{item_name}'",
                "allowed_items": predictor.get_allowed_items()
            }), 400

        # 1) ML prediction (already includes Step 3 safety rule)
        ml = predictor.predict(data)
        final_days = ml["final_days_until_expiry"]
        base_days = ml["base_expiry_days"]

        # 2) AED personalization (Issue B + C)
        user = users_col.find_one({"username": user_id}) or {}
        user_aed = user.get("expiryAdjustment", {}) or {}
        aed_days = apply_aed(user_aed, item_name, category, final_days, base_days)

        # 3) Final expiry date
        exp_date = compute_expiry_date(purchase_date, aed_days)

        return jsonify({
            "item_name": item_name,
            "category": category,
            "base_expiry_days": base_days,
            "model_final_days": final_days,
            "aed_adjusted_days": aed_days,
            "predicted_expiry_date": exp_date
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# ADD FOOD
# ----------------------------------------------------
@food_bp.route("/add", methods=["POST"])
def add_food():
    try:
        data = request.get_json() or {}
        print("📩 /add received:", data)

        user_id = data.get("userId")
        category = data.get("item_category")
        purchase_date = data.get("purchase_date")
        item_name = (data.get("item_name") or "").lower().strip()

        if not user_id or not category:
            return jsonify({"error": "Missing required fields"}), 400

        if not predictor.validate_item(item_name):
            return jsonify({
                "error": f"Unknown item '{item_name}'",
                "allowed_items": predictor.get_allowed_items()
            }), 400

        # 1) ML prediction
        ml = predictor.predict(data)
        final_days = ml["final_days_until_expiry"]
        base_days = ml["base_expiry_days"]

        # 2) AED adjustment (item-level -> category fallback)
        user = users_col.find_one({"username": user_id}) or {}
        user_aed = user.get("expiryAdjustment", {}) or {}
        aed_days = apply_aed(user_aed, item_name, category, final_days, base_days)

        # 3) SCP scoring
        scp = scp_score(aed_days)

        # 4) Expiry date
        expiry = compute_expiry_date(purchase_date, aed_days)

        # 5) Save
        doc = {
            "userId": user_id,
            "foodName": data.get("foodName"),
            "itemName": item_name,
            "category": category,
            "storageType": data.get("storage_type"),
            "purchaseDate": purchase_date,
            "quantity": data.get("quantity"),
            "used_before_exp": data.get("used_before_expiry", data.get("used_before_exp")),

            "base_expiry_days": base_days,
            "model_final_days": final_days,
            "aed_adjusted_days": aed_days,
            "predictedExpiryDate": expiry,
            "scpPriorityScore": scp
        }

        result = foods_col.insert_one(doc)
        doc["_id"] = str(result.inserted_id)

        return jsonify({"message": "Food stored", "food": doc}), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# FEEDBACK (updates BOTH item-level + category-level AED)
# ----------------------------------------------------
@food_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json() or {}
        print("📩 /feedback received:", data)

        food_id = data.get("foodId")
        user_id = data.get("userId")
        status = data.get("feedback")
        actual_days = data.get("actual_days")

        if status not in ("early", "on_time", "late"):
            return jsonify({"error": "Invalid feedback type"}), 400

        # Fetch food record
        food = foods_col.find_one({"_id": ObjectId(food_id)})
        if not food:
            return jsonify({"error": "Food not found"}), 404

        category = (food.get("category") or "").lower().strip()
        item_name = (food.get("itemName") or "").lower().strip()

        predicted_days = food.get("aed_adjusted_days") or food.get("model_final_days") or 0
        base_days = food.get("base_expiry_days") or 7.0

        # Save raw feedback into food doc
        foods_col.update_one(
            {"_id": ObjectId(food_id)},
            {"$set": {"feedback": {"status": status, "actual_days": actual_days}}}
        )

        # Load user AED + stats
        user = users_col.find_one({"username": user_id}) or {}
        user_adj = user.get("expiryAdjustment", {}) or {}
        user_stats = user.get("feedbackStats", {}) or {}

        item_key = f"item:{item_name}"
        cat_key = f"category:{category}"

        prev_item_adj = float(user_adj.get(item_key, 0) or 0)
        prev_cat_adj = float(user_adj.get(cat_key, 0) or 0)

        item_stats = user_stats.get(item_key, {})
        cat_stats = user_stats.get(cat_key, {})

        # Update AED values
        # item adapts faster, category slower
        new_item_adj, new_item_stats = update_aed_single(
            previous_adj=prev_item_adj,
            feedback=status,
            actual_days=float(actual_days),
            predicted_days=float(predicted_days),
            stats=item_stats,
            learning_rate=0.7
        )

        new_cat_adj, new_cat_stats = update_aed_single(
            previous_adj=prev_cat_adj,
            feedback=status,
            actual_days=float(actual_days),
            predicted_days=float(predicted_days),
            stats=cat_stats,
            learning_rate=0.3
        )

        # Save updated AED & stats
        users_col.update_one(
            {"username": user_id},
            {
                "$set": {
                    f"expiryAdjustment.{item_key}": new_item_adj,
                    f"expiryAdjustment.{cat_key}": new_cat_adj,
                    f"feedbackStats.{item_key}": new_item_stats,
                    f"feedbackStats.{cat_key}": new_cat_stats
                }
            },
            upsert=True
        )

        # Show what final AED would produce now (for debugging)
        aed_preview = apply_aed(
            {**user_adj, item_key: new_item_adj, cat_key: new_cat_adj},
            item_name=item_name,
            category=category,
            predicted_days=float(predicted_days),
            base_days=float(base_days)
        )

        return jsonify({
            "message": "Feedback saved (Item + Category AED updated)",
            "item_name": item_name,
            "category": category,
            "predicted_days_used": predicted_days,
            "actual_days": actual_days,
            "previous_item_adj": prev_item_adj,
            "new_item_adj": new_item_adj,
            "previous_cat_adj": prev_cat_adj,
            "new_cat_adj": new_cat_adj,
            "aed_preview_days_now": aed_preview
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# UPDATE
# ----------------------------------------------------
@food_bp.route("/update/<id>", methods=["PUT"])
def update_food(id):
    try:
        data = request.get_json() or {}

        # Validate itemName if updated
        if "itemName" in data:
            name = (data["itemName"] or "").lower().strip()
            if not predictor.validate_item(name):
                return jsonify({
                    "error": f"Unknown item '{name}'",
                    "allowed_items": predictor.get_allowed_items()
                }), 400

        allowed = [
            "foodName", "itemName", "category", "storageType",
            "purchaseDate", "quantity", "used_before_exp"
        ]

        update_fields = {k: data[k] for k in allowed if k in data}

        foods_col.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

        updated = foods_col.find_one({"_id": ObjectId(id)})
        updated["_id"] = str(updated["_id"])

        return jsonify({"updated_food": updated}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# DELETE
# ----------------------------------------------------
@food_bp.route("/delete/<id>", methods=["DELETE"])
def delete_food(id):
    try:
        foods_col.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Food deleted"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
