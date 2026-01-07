# FoodExpiry/routes/food_routes.py

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime, timedelta
import traceback
import math
import re

from FoodExpiry.database.db_connection import foods_col, users_col
from FoodExpiry.models.expiry_predictor import ExpiryPredictor
from FoodExpiry.ml.aed_adjuster import apply_aed, update_aed_single
from FoodExpiry.ml.scp_ranker import scp_score

food_bp = Blueprint("food_bp", __name__)
predictor = ExpiryPredictor()

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------
MIN_FEEDBACK_FOR_PERSONALIZATION = 5


# ----------------------------------------------------
# HELPERS
# ----------------------------------------------------
def canonical_item_name(name: str) -> str:
    """
    Canonicalize user input / DB stored item names so that:
    - case differences don't matter
    - multiple spaces don't matter
    - spaces vs underscores don't matter
    - singular/plural don't fragment the model vocabulary
    """
    if not name:
        return ""

    n = str(name).lower().strip()

    # collapse spaces
    n = re.sub(r"\s+", " ", n)

    # spaces -> underscores
    n = n.replace(" ", "_")

    # exact match
    if predictor.validate_item(n):
        return n

    # singular -> plural
    if predictor.validate_item(n + "s"):
        return n + "s"

    # plural -> singular
    if n.endswith("s") and predictor.validate_item(n[:-1]):
        return n[:-1]

    return n


def canonical_category(name: str) -> str:
    return (str(name).lower().strip() if name is not None else "")


def canonical_storage(name: str) -> str:
    s = (str(name).lower().strip() if name is not None else "")
    if s in ("fridge", "freezer", "pantry"):
        return s
    # fallback (safe)
    return "pantry"


def compute_expiry_date(purchase_date_str: str, days: float):
    """
    Convert predicted days -> YYYY-MM-DD expiry date.
    Using FLOOR makes early spoilage show an earlier calendar date clearly.
    """
    try:
        dt = datetime.strptime(purchase_date_str, "%Y-%m-%d")
        day_int = max(0, int(math.floor(float(days))))
        return (dt + timedelta(days=day_int)).strftime("%Y-%m-%d")
    except Exception:
        return None


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None


def days_left_from_today(expiry_date_str: str, purchase_date_str: str = None) -> int:
    """
    Days left from NOW until expiry.
    If purchase_date is in the future => treat as not active yet (low priority).
    """
    try:
        today = datetime.utcnow().date()

        if purchase_date_str:
            purchase = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
            if today < purchase:
                return 9999  # Not active yet → lowest priority

        exp = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        return (exp - today).days
    except Exception:
        return 9999


# ----------------------------------------------------
# OPTIONS (Dropdowns)
# ----------------------------------------------------
@food_bp.route("/options", methods=["GET"])
def get_options():
    try:
        items = predictor.get_allowed_items()
        categories = [
            "dairy", "meat", "fish", "fruit", "vegetable",
            "grain", "snack", "beverage", "other"
        ]
        return jsonify({"items": items, "categories": categories}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# GET ALL FOODS (Inventory)
# ----------------------------------------------------
@food_bp.route("/", methods=["GET"])
def get_foods():
    foods = list(foods_col.find())
    for f in foods:
        f["_id"] = str(f["_id"])

        final_exp = f.get("finalExpiryDate") or f.get("predictedExpiryDate")
        purchase_date = f.get("purchaseDate") or f.get("purchase_date")

        if final_exp:
            days_left = days_left_from_today(final_exp, purchase_date)
            f["daysLeft"] = days_left
            f["scpPriorityScore_live"] = scp_score(days_left)

    return jsonify(foods), 200


# ----------------------------------------------------
# GET ONE FOOD
# ----------------------------------------------------
@food_bp.route("/one/<id>", methods=["GET"])
def get_one_food(id):
    try:
        f = foods_col.find_one({"_id": ObjectId(id)})
        if not f:
            return jsonify({"error": "Food not found"}), 404
        f["_id"] = str(f["_id"])
        return jsonify(f), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# PREDICT ONLY (From Inventory) + PERSIST RESULTS
# ----------------------------------------------------
@food_bp.route("/predict", methods=["POST"])
def predict_only():
    try:
        data = request.get_json() or {}

        food_id = data.get("foodId")  # inventory record id (recommended)
        user_id = (data.get("userId") or "").strip()

        # from request (fallback)
        item_name = canonical_item_name(data.get("item_name"))
        category = canonical_category(data.get("item_category"))
        purchase_date = data.get("purchase_date")
        printed_expiry = data.get("printed_expiry_date")  # optional
        storage_type = canonical_storage(data.get("storage_type"))

        # ✅ SOURCE OF TRUTH: if foodId exists, use DB values (prevents mismatch)
        if food_id:
            try:
                f = foods_col.find_one({"_id": ObjectId(food_id)})
                if f:
                    item_name = canonical_item_name(f.get("itemName") or item_name)
                    category = canonical_category(f.get("category") or category)
                    purchase_date = f.get("purchaseDate") or purchase_date

                    # ✅ IMPORTANT: storage must come from DB if not provided
                    storage_type = canonical_storage(f.get("storageType") or storage_type)

                    # printed expiry: if not supplied by UI, use stored
                    if printed_expiry is None:
                        printed_expiry = f.get("printedExpiryDate")
            except Exception:
                traceback.print_exc()

        if not user_id or not item_name or not category or not purchase_date:
            return jsonify({"error": "Missing required fields"}), 400

        if not predictor.validate_item(item_name):
            return jsonify({
                "error": f"Unknown item '{item_name}'",
                "allowed_items": predictor.get_allowed_items()
            }), 400

        # IMPORTANT: pass canonical values to predictor (feature alignment)
        data["item_name"] = item_name
        data["item_category"] = category
        data["purchase_date"] = purchase_date
        data["storage_type"] = storage_type  # ✅ CRITICAL FIX

        # ------------------------------------------------
        # 1) BASELINE AEIF (Always active)
        # ------------------------------------------------
        ml = predictor.predict(data)
        baseline_days = float(ml["final_days_until_expiry"])
        base_days = float(ml["base_expiry_days"])
        baseline_expiry = compute_expiry_date(purchase_date, baseline_days)

        # ------------------------------------------------
        # 2) PERSONALIZATION GATE (PER-ITEM: needs 5 feedbacks for same item)
        # ------------------------------------------------
        user = users_col.find_one({"username": user_id}) or {}
        feedback_by_item = user.get("feedbackCountByItem", {}) or {}
        item_feedback_count = int(feedback_by_item.get(item_name, 0))

        personalization_enabled = item_feedback_count >= MIN_FEEDBACK_FOR_PERSONALIZATION

        personalized_days = None
        personalized_expiry = None

        if personalization_enabled:
            user_aed = user.get("expiryAdjustment", {}) or {}
            personalized_days = float(apply_aed(
                user_aed,
                item_name,
                category,
                baseline_days,
                base_days
            ))
            personalized_expiry = compute_expiry_date(purchase_date, personalized_days)

        # ------------------------------------------------
        # 3) PRINTED EXPIRY GATE (Safety upper bound)
        # ------------------------------------------------
        printed_dt = parse_date(printed_expiry) if printed_expiry else None
        model_dt = parse_date(personalized_expiry or baseline_expiry)

        cap_applied = False
        if printed_dt and model_dt and model_dt > printed_dt:
            model_dt = printed_dt
            cap_applied = True

        final_expiry = model_dt.strftime("%Y-%m-%d") if model_dt else None

        # ------------------------------------------------
        # 4) SCP (Decision layer)
        # ------------------------------------------------
        days_left = days_left_from_today(final_expiry, purchase_date) if final_expiry else 9999
        scp = float(scp_score(days_left))

        # ------------------------------------------------
        # 5) Prediction History Entry (last 20)
        # ------------------------------------------------
        history_entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "baseline_days": baseline_days,
            "baseline_expiry_date": baseline_expiry,
            "personalization_enabled": bool(personalization_enabled),
            "personalized_days": personalized_days,
            "personalized_expiry_date": personalized_expiry,
            "final_expiry_date": final_expiry,
            "days_left": int(days_left),
            "scp": scp,
            "printed_expiry_date": printed_expiry,
            "printed_cap_applied": bool(cap_applied)
        }

        # ------------------------------------------------
        # 6) Persist latest + push history (if foodId provided)
        # ------------------------------------------------
        if food_id:
            try:
                foods_col.update_one(
                    {"_id": ObjectId(food_id)},
                    {
                        "$set": {
                            "printedExpiryDate": printed_expiry,
                            "baselineExpiryDate": baseline_expiry,
                            "personalizedExpiryDate": personalized_expiry,
                            "finalExpiryDate": final_expiry,

                            "scpPriorityScore": scp,
                            "daysLeftAtSave": int(days_left),

                            "lastPredictedAt": datetime.utcnow(),
                            "personalization_enabled": bool(personalization_enabled),
                            "printed_cap_applied": bool(cap_applied),

                            "baseline_days": baseline_days,
                            "personalized_days": personalized_days,
                            "base_expiry_days": base_days,

                            # UI clarity
                            "item_feedback_count": int(item_feedback_count),
                            "min_feedback_required": int(MIN_FEEDBACK_FOR_PERSONALIZATION),
                        },
                        "$push": {
                            "predictionHistory": {
                                "$each": [history_entry],
                                "$slice": -20
                            }
                        }
                    }
                )
            except Exception:
                traceback.print_exc()

        needed = max(0, MIN_FEEDBACK_FOR_PERSONALIZATION - item_feedback_count)

        return jsonify({
            "item_name": item_name,
            "category": category,

            # baseline
            "baseline_days": baseline_days,
            "baseline_expiry_date": baseline_expiry,

            # gate info
            "min_required_feedback": MIN_FEEDBACK_FOR_PERSONALIZATION,
            "item_feedback_count": item_feedback_count,
            "feedback_needed": needed,

            # personalization
            "personalization_enabled": personalization_enabled,
            "personalized_days": personalized_days,
            "personalized_expiry_date": personalized_expiry,

            # final
            "printed_expiry_date": printed_expiry,
            "final_expiry_date": final_expiry,
            "printed_cap_applied": cap_applied,

            # scp
            "days_left": int(days_left),
            "scpPriorityScore": scp,

            "message": (
                "Personalized prediction applied"
                if personalization_enabled
                else f"Personalization warming up ({item_feedback_count}/{MIN_FEEDBACK_FOR_PERSONALIZATION} feedbacks for this item)"
            )
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# ADD FOOD (Initial Inventory Entry)
# ----------------------------------------------------
@food_bp.route("/add", methods=["POST"])
def add_food():
    try:
        data = request.get_json() or {}

        user_id = (data.get("userId") or "").strip()
        item_name = canonical_item_name(data.get("item_name"))
        category = canonical_category(data.get("item_category"))
        purchase_date = data.get("purchase_date")
        printed_expiry = data.get("printed_expiry_date")

        if not user_id or not item_name or not category or not purchase_date:
            return jsonify({"error": "Missing required fields"}), 400

        if not predictor.validate_item(item_name):
            return jsonify({
                "error": f"Unknown item '{item_name}'",
                "allowed_items": predictor.get_allowed_items()
            }), 400

        doc = {
            "userId": user_id,
            "foodName": data.get("foodName"),
            "itemName": item_name,
            "category": category,
            "storageType": canonical_storage(data.get("storage_type") or "pantry"),
            "purchaseDate": purchase_date,
            "printedExpiryDate": printed_expiry,
            "quantity": data.get("quantity"),
            "used_before_exp": data.get("used_before_expiry", data.get("used_before_exp")),

            # prediction-related fields (filled on predict)
            "baselineExpiryDate": None,
            "personalizedExpiryDate": None,
            "finalExpiryDate": None,
            "scpPriorityScore": None,
            "predictionHistory": [],

            "createdAt": datetime.utcnow()
        }

        result = foods_col.insert_one(doc)
        doc["_id"] = str(result.inserted_id)

        return jsonify({
            "message": "Successfully the item has been added to the inventory. Please check the inventory to predict the expiry date.",
            "food": doc
        }), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# FEEDBACK (Learning Loop – AEIF Core)
# ----------------------------------------------------
@food_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json() or {}

        food_id = data.get("foodId")
        user_id = (data.get("userId") or "").strip()
        status = data.get("feedback")
        actual_days = data.get("actual_days")

        if not food_id or not user_id:
            return jsonify({"error": "Missing foodId or userId"}), 400

        if status not in ("early", "on_time", "late"):
            return jsonify({"error": "Invalid feedback type"}), 400

        try:
            actual_days = float(actual_days)
        except Exception:
            return jsonify({"error": "actual_days must be a number"}), 400

        food = foods_col.find_one({"_id": ObjectId(food_id)})
        if not food:
            return jsonify({"error": "Food not found"}), 404

        category = canonical_category(food.get("category"))
        item_name = canonical_item_name(food.get("itemName"))

        predicted_days = (
            food.get("personalized_days")
            or food.get("baseline_days")
            or food.get("aed_adjusted_days")
            or food.get("model_final_days")
            or 0
        )

        try:
            predicted_days = float(predicted_days)
        except Exception:
            predicted_days = 0.0

        foods_col.update_one(
            {"_id": ObjectId(food_id)},
            {"$set": {"feedback": {"status": status, "actual_days": actual_days}}}
        )

        user = users_col.find_one({"username": user_id}) or {}
        user_adj = user.get("expiryAdjustment", {}) or {}
        user_stats = user.get("feedbackStats", {}) or {}
        feedback_by_item = user.get("feedbackCountByItem", {}) or {}

        item_key = f"item:{item_name}"
        cat_key = f"category:{category}"

        new_item_adj, new_item_stats = update_aed_single(
            user_adj.get(item_key, 0),
            status,
            actual_days,
            predicted_days,
            user_stats.get(item_key, {}),
            learning_rate=0.7
        )

        new_cat_adj, new_cat_stats = update_aed_single(
            user_adj.get(cat_key, 0),
            status,
            actual_days,
            predicted_days,
            user_stats.get(cat_key, {}),
            learning_rate=0.3
        )

        before_item_count = int(feedback_by_item.get(item_name, 0))
        after_item_count = before_item_count + 1
        activated_now = (
            before_item_count < MIN_FEEDBACK_FOR_PERSONALIZATION
            and after_item_count >= MIN_FEEDBACK_FOR_PERSONALIZATION
        )

        users_col.update_one(
            {"username": user_id},
            {
                "$set": {
                    f"expiryAdjustment.{item_key}": new_item_adj,
                    f"expiryAdjustment.{cat_key}": new_cat_adj,
                    f"feedbackStats.{item_key}": new_item_stats,
                    f"feedbackStats.{cat_key}": new_cat_stats,
                    f"feedbackCountByItem.{item_name}": after_item_count,
                },
                "$inc": {"totalFeedbackCount": 1}
            },
            upsert=True
        )

        return jsonify({
            "message": "Feedback saved and personalization model updated",
            "userId": user_id,
            "item_name": item_name,
            "category": category,
            "min_required_feedback": MIN_FEEDBACK_FOR_PERSONALIZATION,
            "item_feedback_count_after": after_item_count,
            "feedback_needed": max(0, MIN_FEEDBACK_FOR_PERSONALIZATION - after_item_count),
            "personalization_activated_now": bool(activated_now),
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# UPDATE FOOD
# ----------------------------------------------------
@food_bp.route("/update/<id>", methods=["PUT"])
def update_food(id):
    try:
        data = request.get_json() or {}

        if "item_name" in data and "itemName" not in data:
            data["itemName"] = data["item_name"]
        if "item_category" in data and "category" not in data:
            data["category"] = data["item_category"]
        if "storage_type" in data and "storageType" not in data:
            data["storageType"] = data["storage_type"]
        if "purchase_date" in data and "purchaseDate" not in data:
            data["purchaseDate"] = data["purchase_date"]
        if "used_before_expiry" in data and "used_before_exp" not in data:
            data["used_before_exp"] = data["used_before_expiry"]
        if "printed_expiry_date" in data and "printedExpiryDate" not in data:
            data["printedExpiryDate"] = data["printed_expiry_date"]

        if "itemName" in data:
            name = canonical_item_name(data["itemName"])
            if not predictor.validate_item(name):
                return jsonify({
                    "error": f"Unknown item '{name}'",
                    "allowed_items": predictor.get_allowed_items()
                }), 400
            data["itemName"] = name

        if "category" in data:
            data["category"] = canonical_category(data["category"])

        if "storageType" in data:
            data["storageType"] = canonical_storage(data["storageType"])

        allowed = [
            "foodName", "itemName", "category", "storageType",
            "purchaseDate", "quantity", "used_before_exp", "printedExpiryDate"
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
# DELETE FOOD
# ----------------------------------------------------
@food_bp.route("/delete/<id>", methods=["DELETE"])
def delete_food(id):
    try:
        foods_col.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Food deleted"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
