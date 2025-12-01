from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime, timedelta
import traceback

from FoodExpiry.database.db_connection import foods_col, users_col
from FoodExpiry.models.expiry_predictor import ExpiryPredictor
from FoodExpiry.ml.aed_adjuster import apply_aed
from FoodExpiry.ml.scp_ranker import scp_score

food_bp = Blueprint("food_bp", __name__)
predictor = ExpiryPredictor()


# ----------------------------------------------------
# Helper – calculate expiry date
# ----------------------------------------------------
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
        data = request.get_json()
        print("📩 /predict received:", data)

        user_id = data.get("userId")
        category = data.get("item_category")
        purchase_date = data.get("purchase_date")
        item_name = (data.get("item_name") or "").lower().strip()

        if not user_id or not category:
            return jsonify({"error": "Missing required fields"}), 400

        # 0. Validate item name (one-hot)
        if not predictor.validate_item(item_name):
            return jsonify({
                "error": f"Unknown item_name '{item_name}'",
                "allowed_items": predictor.get_allowed_items()
            }), 400

        # 1. ML prediction (final_days)
        ml = predictor.predict(data)
        final_days = ml["final_days_until_expiry"]

        # 2. AED personalization
        user = users_col.find_one({"username": user_id})
        user_aed = user.get("expiryAdjustment", {}) if user else {}
        aed_days = apply_aed(user_aed, category, final_days)

        # 3. Final expiry date
        exp_date = compute_expiry_date(purchase_date, aed_days)

        return jsonify({
            "item_name": item_name,
            "category": category,
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
        data = request.get_json()
        print("📩 /add received:", data)

        user_id = data.get("userId")
        category = data.get("item_category")
        purchase_date = data.get("purchase_date")
        item_name = (data.get("item_name") or "").lower().strip()

        if not user_id or not category:
            return jsonify({"error": "Missing required fields"}), 400

        # Validate item
        if not predictor.validate_item(item_name):
            return jsonify({
                "error": f"Unknown item '{item_name}'",
                "allowed_items": predictor.get_allowed_items()
            }), 400

        # 1. ML prediction
        ml = predictor.predict(data)
        final_days = ml["final_days_until_expiry"]

        # 2. AED adjustment
        user = users_col.find_one({"username": user_id})
        user_aed = user.get("expiryAdjustment", {}) if user else {}
        aed_days = apply_aed(user_aed, category, final_days)

        # 3. SCP scoring
        scp = scp_score(aed_days)

        # 4. Expiry date
        expiry = compute_expiry_date(purchase_date, aed_days)

        # 5. Save
        doc = {
            "userId": user_id,
            "foodName": data.get("foodName"),
            "itemName": item_name,
            "category": category,
            "storageType": data.get("storage_type"),

            "purchaseDate": purchase_date,
            "quantity": data.get("quantity"),
            "used_before_exp": data.get("used_before_expiry"),

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
# FEEDBACK
# ----------------------------------------------------
@food_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json()
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

        category = food["category"]
        predicted_days = food.get("aed_adjusted_days") or food.get("model_final_days")

        # -----------------------------------------------------------
        # Save raw feedback in food document
        # -----------------------------------------------------------
        foods_col.update_one(
            {"_id": ObjectId(food_id)},
            {"$set": {"feedback": {"status": status, "actual_days": actual_days}}}
        )

        # -----------------------------------------------------------
        # Load user AED + feedback stats
        # -----------------------------------------------------------
        user = users_col.find_one({"username": user_id}) or {}
        user_adj = user.get("expiryAdjustment", {})
        stats = user.get("feedbackStats", {}).get(category, {})

        previous_adj = user_adj.get(category, 0)

        # -----------------------------------------------------------
        # Compute NEW adjustment using Advanced AED
        # -----------------------------------------------------------
        from FoodExpiry.ml.aed_adjuster import update_aed

        new_adj, new_stats = update_aed(
            previous_adj=previous_adj,
            category_feedback=status,
            actual_days=actual_days,
            predicted_days=predicted_days,
            stats=stats
        )

        # -----------------------------------------------------------
        # Save updated AED & stats
        # -----------------------------------------------------------
        users_col.update_one(
            {"username": user_id},
            {
                "$set": {
                    f"expiryAdjustment.{category}": new_adj,
                    f"feedbackStats.{category}": new_stats
                }
            },
            upsert=True
        )

        return jsonify({
            "message": "Feedback saved (Advanced AED applied)",
            "category": category,
            "previous_adj": previous_adj,
            "new_adj": new_adj,
            "previous_stats": stats,
            "updated_stats": new_stats
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
        data = request.get_json()

        # Validate itemName if updated
        if "itemName" in data:
            name = data["itemName"].lower().strip()
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
