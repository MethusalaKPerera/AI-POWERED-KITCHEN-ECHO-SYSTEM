# FoodExpiry/routes/food_routes.py

from flask import Blueprint, request, jsonify, Response, send_file
from bson import ObjectId
from datetime import datetime, timedelta
import traceback
import math
import re
import io
import csv

from FoodExpiry.database.db_connection import foods_col, users_col
from FoodExpiry.models.expiry_predictor import ExpiryPredictor
from FoodExpiry.ml.aed_adjuster import apply_aed, update_aed_single
from FoodExpiry.ml.scp_ranker import scp_score

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

food_bp = Blueprint("food_bp", __name__)
predictor = ExpiryPredictor()

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------
MIN_FEEDBACK_FOR_PERSONALIZATION = 5

# ----------------------------------------------------
# ENVIRONMENT (PP2) — Storage-based bounds + Sri Lanka region humidity presets
# ----------------------------------------------------
# ✅ UPDATED (necessary): Support BOTH your older "climate zones" and your UI provinces
REGION_HUMIDITY_PRESETS = {
    # climate-zone style (kept)
    "wet_zone": 80.0,
    "intermediate_zone": 70.0,
    "dry_zone": 60.0,
    "hill_country": 75.0,

    # province style (matches Inventory.jsx dropdown)
    "western": 78.0,
    "central": 72.0,
    "southern": 80.0,
    "northern": 70.0,
    "eastern": 75.0,
    "north western": 76.0,
    "north central": 68.0,
    "uva": 74.0,
    "sabaragamuwa": 79.0,
}

# These match the augmentation ranges (safer to keep within trained distribution)
STORAGE_ENV_BOUNDS = {
    "freezer": {"temp_min": -20.0, "temp_max": -16.0, "hum_min": 85.0, "hum_max": 95.0},
    "fridge": {"temp_min": 3.0, "temp_max": 5.0, "hum_min": 60.0, "hum_max": 70.0},
    "pantry": {"temp_min": 26.0, "temp_max": 30.0, "hum_min": 70.0, "hum_max": 85.0},
}


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


def clamp_float(v, lo, hi, fallback=None):
    try:
        x = float(v)
        return max(lo, min(x, hi))
    except Exception:
        return fallback


def compute_expiry_date(purchase_date_str: str, days: float):
    """
    Convert predicted days -> YYYY-MM-DD expiry date.
    Using CEIL makes early spoilage show an earlier calendar date clearly.
    """
    try:
        dt = datetime.strptime(purchase_date_str, "%Y-%m-%d")
        day_int = max(0, int(math.ceil(float(days))))
        return (dt + timedelta(days=day_int)).strftime("%Y-%m-%d")
    except Exception:
        return None


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_ts_iso(ts: str):
    """
    predictionHistory.ts is saved like: 2026-02-10T10:12:33.123Z
    """
    try:
        if not ts:
            return None
        s = str(ts).strip()
        if s.endswith("Z"):
            s = s[:-1]
        # allow ms or no ms
        try:
            return datetime.fromisoformat(s)
        except Exception:
            # fallback common format
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
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


def _range_from_query(args):
    """
    Supported:
      - ?period=7d or 30d (default 30d)
      - OR ?start=YYYY-MM-DD&end=YYYY-MM-DD
    Returns: (start_dt, end_dt) UTC datetimes (end exclusive)
    """
    start = args.get("start")
    end = args.get("end")
    period = (args.get("period") or "30d").strip().lower()

    now = datetime.utcnow()

    if start and end:
        try:
            s = datetime.strptime(start, "%Y-%m-%d")
            e = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
            return s, e
        except Exception:
            pass

    if period == "7d":
        return now - timedelta(days=7), now + timedelta(seconds=1)
    if period == "30d":
        return now - timedelta(days=30), now + timedelta(seconds=1)

    # fallback default
    return now - timedelta(days=30), now + timedelta(seconds=1)


def _history_rows_for_user(user_id: str, item: str = None, storage: str = None, start_dt=None, end_dt=None):
    """
    Flatten foods.predictionHistory into rows:
      { ts, itemName, category, storageType, baseline_days, personalized_days, final_expiry_date,
        days_left, scp, personalization_enabled, printed_cap_applied, printed_expiry_date, foodId }
    """
    q = {"userId": user_id}
    if item and item != "all":
        q["itemName"] = canonical_item_name(item)
    if storage and storage != "all":
        q["storageType"] = canonical_storage(storage)

    foods = list(foods_col.find(q))
    rows = []

    for f in foods:
        food_id = str(f.get("_id"))
        item_name = f.get("itemName") or f.get("item_name")
        cat = f.get("category") or f.get("item_category")
        st = f.get("storageType") or f.get("storage_type")

        hist = f.get("predictionHistory", []) or []
        for h in hist:
            ts = h.get("ts")
            ts_dt = parse_ts_iso(ts)
            if not ts_dt:
                continue

            if start_dt and ts_dt < start_dt:
                continue
            if end_dt and ts_dt >= end_dt:
                continue

            rows.append({
                "ts": ts,
                "ts_dt": ts_dt,
                "foodId": food_id,

                "item_name": item_name,
                "category": cat,
                "storage_type": st,

                "baseline_days": h.get("baseline_days"),
                "baseline_expiry_date": h.get("baseline_expiry_date"),

                "personalization_enabled": bool(h.get("personalization_enabled")),
                "personalized_days": h.get("personalized_days"),
                "personalized_expiry_date": h.get("personalized_expiry_date"),

                "final_expiry_date": h.get("final_expiry_date"),
                "days_left": h.get("days_left"),
                "scp": h.get("scp"),

                "printed_expiry_date": h.get("printed_expiry_date"),
                "printed_cap_applied": bool(h.get("printed_cap_applied")),
            })

    # sort newest first
    rows.sort(key=lambda r: r["ts_dt"], reverse=True)
    return rows


def _bucket_days_left(d):
    """
    For urgency chart:
      expired (<0), 0-3, 4-7, 8+
    """
    try:
        d = int(d)
    except Exception:
        return "unknown"

    if d < 0:
        return "expired"
    if d <= 3:
        return "0-3"
    if d <= 7:
        return "4-7"
    return "8+"


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
    try:
        # ✅ NEW (backward compatible): allow optional filter by userId
        user_id = (request.args.get("userId") or request.args.get("user_id") or "").strip()
        q = {"userId": user_id} if user_id else {}

        try:
            foods = list(foods_col.find(q))
        except Exception as e:
            traceback.print_exc()
            return jsonify({
                "error": "FoodExpiry DB connection failed",
                "message": str(e),
            }), 500

        for f in foods:
            f["_id"] = str(f["_id"])

            final_exp = f.get("finalExpiryDate") or f.get("predictedExpiryDate")
            purchase_date = f.get("purchaseDate") or f.get("purchase_date")

            if final_exp:
                days_left = days_left_from_today(final_exp, purchase_date)
                f["daysLeft"] = days_left
                f["scpPriorityScore_live"] = scp_score(days_left)

        return jsonify(foods), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "FoodExpiry failed to load foods",
            "message": str(e),
        }), 500


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

        # NEW (PP2): Environment inputs (optional)
        region = (data.get("region") or data.get("climate_zone") or "").strip().lower() or None
        req_temp = data.get("storage_temperature_c", None)
        req_hum = data.get("storage_humidity_pct", None)

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

                    # if region/env not supplied by UI, you may optionally reuse last saved env
                    if region is None:
                        region = (f.get("region") or "").strip().lower() or None
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
        # (PP2) Resolve humidity from region preset if humidity not provided
        # ------------------------------------------------
        if req_hum is None and region in REGION_HUMIDITY_PRESETS:
            req_hum = REGION_HUMIDITY_PRESETS[region]

        # ------------------------------------------------
        # (PP2) Clamp env values to trained bounds per storage type (if provided)
        # ------------------------------------------------
        bounds = STORAGE_ENV_BOUNDS.get(storage_type, STORAGE_ENV_BOUNDS["pantry"])

        # If temperature/humidity are provided, clamp them.
        # If not provided, predictor will fallback to its defaults.
        if req_temp is not None:
            clamped_temp = clamp_float(req_temp, bounds["temp_min"], bounds["temp_max"], fallback=None)
            if clamped_temp is not None:
                data["storage_temperature_c"] = clamped_temp

        if req_hum is not None:
            clamped_hum = clamp_float(req_hum, bounds["hum_min"], bounds["hum_max"], fallback=None)
            if clamped_hum is not None:
                data["storage_humidity_pct"] = clamped_hum

        # keep region in data (optional)
        if region:
            data["region"] = region

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
            "printed_cap_applied": bool(cap_applied),

            # (PP2) store environment used for this prediction (helps panel questions + reproducibility)
            "region": region,
            "storage_temperature_c": data.get("storage_temperature_c", None),
            "storage_humidity_pct": data.get("storage_humidity_pct", None),
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

                            # (PP2) store last used env at item-level too
                            "region": region,
                            "storage_temperature_c": data.get("storage_temperature_c", None),
                            "storage_humidity_pct": data.get("storage_humidity_pct", None),
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

            # (PP2) echo back environment used (these are clamped if needed)
            "region": region,
            "storage_temperature_c": data.get("storage_temperature_c", None),
            "storage_humidity_pct": data.get("storage_humidity_pct", None),

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

            # (PP2 optional) persist region env chosen at add-time (can be empty)
            "region": (data.get("region") or "").strip().lower() or None,
            "storage_temperature_c": data.get("storage_temperature_c", None),
            "storage_humidity_pct": data.get("storage_humidity_pct", None),

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


# ====================================================
# USER + ITEM ANALYTICS (Option B)
# ====================================================

@food_bp.route("/analytics/summary", methods=["GET"])
def analytics_summary():
    """
    Query:
      user_id=U001
      item=all | apple
      storage=all | fridge/freezer/pantry
      period=7d|30d OR start/end

    Returns KPIs + distributions for dashboard cards.
    """
    try:
        user_id = (request.args.get("user_id") or request.args.get("userId") or "").strip()
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        item = (request.args.get("item") or "all").strip().lower()
        storage = (request.args.get("storage") or "all").strip().lower()
        start_dt, end_dt = _range_from_query(request.args)

        rows = _history_rows_for_user(user_id, item=item, storage=storage, start_dt=start_dt, end_dt=end_dt)

        user = users_col.find_one({"username": user_id}) or {}
        total_feedback = int(user.get("totalFeedbackCount", 0) or 0)

        total_predictions = len(rows)
        personalized_count = sum(1 for r in rows if r.get("personalization_enabled"))
        printed_caps = sum(1 for r in rows if r.get("printed_cap_applied"))

        # AED strength proxy: average delta between baseline_days and personalized_days (where available)
        deltas = []
        for r in rows:
            bd = r.get("baseline_days")
            pd = r.get("personalized_days")
            if bd is None or pd is None:
                continue
            try:
                deltas.append(float(pd) - float(bd))
            except Exception:
                pass
        avg_aed_delta = (sum(deltas) / len(deltas)) if deltas else 0.0

        # urgency buckets
        urgency = {"expired": 0, "0-3": 0, "4-7": 0, "8+": 0, "unknown": 0}
        for r in rows:
            b = _bucket_days_left(r.get("days_left"))
            urgency[b] = urgency.get(b, 0) + 1

        # personalization status for selected item
        feedback_by_item = user.get("feedbackCountByItem", {}) or {}
        if item != "all":
            item_key = canonical_item_name(item)
            item_fb = int(feedback_by_item.get(item_key, 0) or 0)
            personalization_ready = item_fb >= MIN_FEEDBACK_FOR_PERSONALIZATION
            needed = max(0, MIN_FEEDBACK_FOR_PERSONALIZATION - item_fb)
        else:
            item_fb = None
            personalization_ready = None
            needed = None

        return jsonify({
            "user_id": user_id,
            "filters": {
                "item": item,
                "storage": storage,
                "start": start_dt.isoformat() + "Z",
                "end": end_dt.isoformat() + "Z",
            },
            "kpis": {
                "total_predictions": total_predictions,
                "personalized_predictions": personalized_count,
                "printed_caps_applied": printed_caps,
                "total_feedback_count": total_feedback,
                "avg_aed_delta_days": round(avg_aed_delta, 3),
            },
            "personalization": {
                "min_feedback_required": MIN_FEEDBACK_FOR_PERSONALIZATION,
                "item_feedback_count": item_fb,
                "personalization_ready": personalization_ready,
                "feedback_needed": needed,
            },
            "urgency_distribution": urgency,
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@food_bp.route("/analytics/timeseries", methods=["GET"])
def analytics_timeseries():
    """
    Returns daily aggregated series for charts.
    Query:
      user_id, item=all|apple, storage=all|fridge, period=7d|30d OR start/end

    Output:
      series: [{date, predictions, avg_baseline_days, avg_personalized_days, avg_scp, expired_count, urgent_count}]
    """
    try:
        user_id = (request.args.get("user_id") or request.args.get("userId") or "").strip()
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        item = (request.args.get("item") or "all").strip().lower()
        storage = (request.args.get("storage") or "all").strip().lower()
        start_dt, end_dt = _range_from_query(request.args)

        rows = _history_rows_for_user(user_id, item=item, storage=storage, start_dt=start_dt, end_dt=end_dt)

        # group by date
        by_date = {}
        for r in rows:
            d = r["ts_dt"].date().strftime("%Y-%m-%d")
            by_date.setdefault(d, []).append(r)

        # build sorted series
        keys = sorted(by_date.keys())
        series = []
        for d in keys:
            bucket = by_date[d]
            preds = len(bucket)

            def _avg(vals):
                vals = [v for v in vals if v is not None]
                if not vals:
                    return None
                try:
                    vals = [float(x) for x in vals]
                    return sum(vals) / len(vals)
                except Exception:
                    return None

            avg_baseline = _avg([x.get("baseline_days") for x in bucket])
            avg_personal = _avg([x.get("personalized_days") for x in bucket if x.get("personalization_enabled")])
            avg_scp = _avg([x.get("scp") for x in bucket])

            expired_count = sum(1 for x in bucket if (x.get("days_left") is not None and int(x.get("days_left")) < 0))
            urgent_count = sum(1 for x in bucket if (x.get("days_left") is not None and 0 <= int(x.get("days_left")) <= 3))

            series.append({
                "date": d,
                "predictions": preds,
                "avg_baseline_days": None if avg_baseline is None else round(avg_baseline, 3),
                "avg_personalized_days": None if avg_personal is None else round(avg_personal, 3),
                "avg_scp": None if avg_scp is None else round(avg_scp, 3),
                "expired_count": int(expired_count),
                "urgent_count": int(urgent_count),
            })

        return jsonify({
            "user_id": user_id,
            "filters": {
                "item": item,
                "storage": storage,
                "start": start_dt.isoformat() + "Z",
                "end": end_dt.isoformat() + "Z",
            },
            "series": series
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@food_bp.route("/analytics/history", methods=["GET"])
def analytics_history():
    """
    Flat history rows for table.
    Query:
      user_id, item=all|apple, storage=all|fridge, period=7d|30d OR start/end
      page=1, page_size=25
    """
    try:
        user_id = (request.args.get("user_id") or request.args.get("userId") or "").strip()
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        item = (request.args.get("item") or "all").strip().lower()
        storage = (request.args.get("storage") or "all").strip().lower()
        start_dt, end_dt = _range_from_query(request.args)

        page = int(request.args.get("page", 1) or 1)
        page_size = int(request.args.get("page_size", 25) or 25)
        page = max(1, page)
        page_size = min(max(5, page_size), 200)

        rows = _history_rows_for_user(user_id, item=item, storage=storage, start_dt=start_dt, end_dt=end_dt)
        total = len(rows)

        start_i = (page - 1) * page_size
        end_i = start_i + page_size
        slice_rows = rows[start_i:end_i]

        out = []
        for r in slice_rows:
            out.append({
                "ts": r.get("ts"),
                "foodId": r.get("foodId"),
                "item_name": r.get("item_name"),
                "category": r.get("category"),
                "storage_type": r.get("storage_type"),

                "baseline_days": r.get("baseline_days"),
                "personalization_enabled": bool(r.get("personalization_enabled")),
                "personalized_days": r.get("personalized_days"),

                "final_expiry_date": r.get("final_expiry_date"),
                "days_left": r.get("days_left"),
                "scp": r.get("scp"),

                "printed_expiry_date": r.get("printed_expiry_date"),
                "printed_cap_applied": bool(r.get("printed_cap_applied")),
            })

        return jsonify({
            "user_id": user_id,
            "filters": {
                "item": item,
                "storage": storage,
                "start": start_dt.isoformat() + "Z",
                "end": end_dt.isoformat() + "Z",
            },
            "page": page,
            "page_size": page_size,
            "total": total,
            "rows": out
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@food_bp.route("/analytics/export/csv", methods=["GET"])
def analytics_export_csv():
    """
    Download CSV for user or item history.
    Query:
      user_id, item=all|apple, storage=all|fridge, period=7d|30d OR start/end
    """
    try:
        user_id = (request.args.get("user_id") or request.args.get("userId") or "").strip()
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        item = (request.args.get("item") or "all").strip().lower()
        storage = (request.args.get("storage") or "all").strip().lower()
        start_dt, end_dt = _range_from_query(request.args)

        rows = _history_rows_for_user(user_id, item=item, storage=storage, start_dt=start_dt, end_dt=end_dt)

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "ts", "user_id", "foodId", "item_name", "category", "storage_type",
            "baseline_days", "baseline_expiry_date",
            "personalization_enabled", "personalized_days", "personalized_expiry_date",
            "final_expiry_date", "days_left", "scp",
            "printed_expiry_date", "printed_cap_applied"
        ])

        for r in rows:
            writer.writerow([
                r.get("ts"), user_id, r.get("foodId"),
                r.get("item_name"), r.get("category"), r.get("storage_type"),
                r.get("baseline_days"), r.get("baseline_expiry_date"),
                r.get("personalization_enabled"), r.get("personalized_days"), r.get("personalized_expiry_date"),
                r.get("final_expiry_date"), r.get("days_left"), r.get("scp"),
                r.get("printed_expiry_date"), r.get("printed_cap_applied")
            ])

        csv_data = output.getvalue().encode("utf-8")
        output.close()

        filename = f"food_expiry_history_{user_id}_{item}_{storage}.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@food_bp.route("/analytics/export/pdf", methods=["GET"])
def analytics_export_pdf():
    if not REPORTLAB_AVAILABLE:
        return jsonify({
            "error": "PDF generation unavailable",
            "message": "The 'reportlab' library is not installed on the server."
        }), 503

    """
    Download a simple research-ready PDF report (KPI + distributions + recent rows).
    Query:
      user_id, item=all|apple, storage=all|fridge, period=7d|30d OR start/end
    """
    try:
        user_id = (request.args.get("user_id") or request.args.get("userId") or "").strip()
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        item = (request.args.get("item") or "all").strip().lower()
        storage = (request.args.get("storage") or "all").strip().lower()
        start_dt, end_dt = _range_from_query(request.args)

        # get data
        rows = _history_rows_for_user(user_id, item=item, storage=storage, start_dt=start_dt, end_dt=end_dt)
        user = users_col.find_one({"username": user_id}) or {}
        total_feedback = int(user.get("totalFeedbackCount", 0) or 0)

        total_predictions = len(rows)
        personalized_count = sum(1 for r in rows if r.get("personalization_enabled"))
        caps = sum(1 for r in rows if r.get("printed_cap_applied"))

        urgency = {"expired": 0, "0-3": 0, "4-7": 0, "8+": 0, "unknown": 0}
        for r in rows:
            b = _bucket_days_left(r.get("days_left"))
            urgency[b] = urgency.get(b, 0) + 1

        # AED delta avg
        deltas = []
        for r in rows:
            bd = r.get("baseline_days")
            pd = r.get("personalized_days")
            if bd is None or pd is None:
                continue
            try:
                deltas.append(float(pd) - float(bd))
            except Exception:
                pass
        avg_delta = (sum(deltas) / len(deltas)) if deltas else 0.0

        # build PDF
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        w, h = A4

        y = h - 2.2 * cm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, y, "Food Expiry Predictor — Analytics Report")
        y -= 0.8 * cm

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, f"User: {user_id} | Item: {item} | Storage: {storage}")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Range: {start_dt.date()} to {end_dt.date()}")
        y -= 0.9 * cm

        # KPIs
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Key Metrics")
        y -= 0.6 * cm

        c.setFont("Helvetica", 10)
        lines = [
            f"Total predictions: {total_predictions}",
            f"Personalized predictions (AED applied): {personalized_count}",
            f"Printed-expiry safety caps applied: {caps}",
            f"Total feedback count (user): {total_feedback}",
            f"Average AED delta (days): {avg_delta:.2f}",
        ]
        for ln in lines:
            c.drawString(2 * cm, y, f"• {ln}")
            y -= 0.45 * cm

        y -= 0.2 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Urgency Distribution (Days Left Buckets)")
        y -= 0.6 * cm

        # simple distribution bars
        max_val = max(urgency.values()) if urgency else 1
        bar_w = 12 * cm
        for k in ["expired", "0-3", "4-7", "8+", "unknown"]:
            val = int(urgency.get(k, 0))
            frac = (val / max_val) if max_val else 0
            c.setFont("Helvetica", 10)
            c.drawString(2 * cm, y, f"{k}: {val}")
            c.rect(6 * cm, y - 0.15 * cm, bar_w * frac, 0.35 * cm, stroke=0, fill=1)
            y -= 0.55 * cm

        y -= 0.2 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Recent Prediction History (Top 12)")
        y -= 0.6 * cm

        # table header
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2 * cm, y, "Date")
        c.drawString(4.8 * cm, y, "Item")
        c.drawString(9.8 * cm, y, "Final Expiry")
        c.drawString(13.2 * cm, y, "Days Left")
        y -= 0.35 * cm
        c.line(2 * cm, y, 19 * cm, y)
        y -= 0.35 * cm

        c.setFont("Helvetica", 9)
        for r in rows[:12]:
            dt = r["ts_dt"].strftime("%Y-%m-%d")
            item_name = str(r.get("item_name") or "")[:20]
            final_exp = str(r.get("final_expiry_date") or "-")
            days_left = str(r.get("days_left") if r.get("days_left") is not None else "-")

            c.drawString(2 * cm, y, dt)
            c.drawString(4.8 * cm, y, item_name)
            c.drawString(9.8 * cm, y, final_exp)
            c.drawString(13.2 * cm, y, days_left)
            y -= 0.45 * cm

            if y < 2.2 * cm:
                c.showPage()
                y = h - 2.2 * cm
                c.setFont("Helvetica", 10)

        # explanation
        if y < 4.0 * cm:
            c.showPage()
            y = h - 2.2 * cm

        y -= 0.3 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "How the system works (short explanation)")
        y -= 0.6 * cm
        c.setFont("Helvetica", 10)
        expl = [
            "1) AEIF baseline calculates expiry from base expiry knowledge + storage context.",
            f"2) AED personalization activates after ≥ {MIN_FEEDBACK_FOR_PERSONALIZATION} feedbacks for the same item.",
            "3) Printed expiry date acts as a safety cap (never recommend beyond printed date).",
            "4) SCP ranks urgency using days left to generate a use-first list.",
            "5) predictionHistory stores predictions over time to prove personalization improvements.",
        ]
        for ln in expl:
            c.drawString(2 * cm, y, f"• {ln}")
            y -= 0.45 * cm

        c.showPage()
        c.save()

        buf.seek(0)
        filename = f"food_expiry_report_{user_id}_{item}_{storage}.pdf"
        return send_file(
            buf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500