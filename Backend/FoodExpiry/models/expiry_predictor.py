# FoodExpiry/models/expiry_predictor.py

import os
import pandas as pd
try:
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except Exception as e:
    print(f"[WARN] CatBoost could not be imported: {e}")
    CATBOOST_AVAILABLE = False

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
MAX_EXPIRY_DAYS = 30.0  # safety upper bound only (not used for scaling)

# ✅ REQUIRED PATHS (as you requested)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "expiry_model_predictor.cbm")
FEATURE_PATH = os.path.join(os.path.dirname(__file__), "feature_columns_predictor.txt")
BASE_EXPIRY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "item_base_expiry_days.csv")


class ExpiryPredictor:
    def __init__(self):
        # -------------------------------------------------
        # Load trained CatBoost model
        # -------------------------------------------------
        self.model = None
        if CATBOOST_AVAILABLE:
            try:
                self.model = CatBoostRegressor()
                self.model.load_model(MODEL_PATH)
                print("[OK] ExpiryPredictor: CatBoost model loaded.")
            except Exception as e:
                print(f"[WARN] ExpiryPredictor: Failed to load model from {MODEL_PATH}: {e}")
                self.model = None
        else:
            print("[WARN] ExpiryPredictor: Running in fallback mode (CatBoost unavailable).")

        # -------------------------------------------------
        # Load feature column order (CRITICAL)
        # -------------------------------------------------
        self.feature_columns = []
        try:
            if os.path.exists(FEATURE_PATH):
                with open(FEATURE_PATH, "r", encoding="utf-8") as f:
                    self.feature_columns = [line.strip() for line in f.readlines() if line.strip()]
            else:
                print(f"[WARN] Feature path not found: {FEATURE_PATH}")
        except Exception as e:
            print(f"[WARN] Error loading features: {e}")

        # -------------------------------------------------
        # Load base expiry lookup table
        # -------------------------------------------------
        base_df = pd.read_csv(BASE_EXPIRY_PATH)
        base_df["item_name"] = base_df["item_name"].astype(str).str.lower().str.strip()

        self.base_expiry_map = {}
        for _, r in base_df.iterrows():
            self.base_expiry_map[r["item_name"]] = {
                "fridge": float(r.get("base_fridge_days", 7) or 7),
                "freezer": float(r.get("base_freezer_days", 30) or 30),
                "pantry": float(r.get("base_pantry_days", 7) or 7),
            }

        # -------------------------------------------------
        # Allowed food items (derived from one-hot columns)
        # -------------------------------------------------
        self.allowed_food_items = sorted(
            c.replace("food_", "", 1)
            for c in self.feature_columns
            if c.startswith("food_")
        )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    def validate_item(self, item_name: str) -> bool:
        if not item_name:
            return False
        return f"food_{item_name.lower().strip()}" in self.feature_columns

    def get_allowed_items(self):
        return self.allowed_food_items

    # ---------------------------------------------------------
    # BASE EXPIRY LOOKUP
    # ---------------------------------------------------------
    def get_base_expiry_days(self, item_name: str, storage_type: str) -> float:
        item = (item_name or "").lower().strip()
        storage = (storage_type or "pantry").lower().strip()

        if storage not in ("fridge", "freezer", "pantry"):
            storage = "pantry"

        return float(self.base_expiry_map.get(item, {}).get(storage, 7.0))

    # ---------------------------------------------------------
    # DEFAULT ENVIRONMENT (Sri Lanka)
    # ---------------------------------------------------------
    def _default_environment(self, storage: str):
        storage = (storage or "pantry").lower().strip()
        if storage == "freezer":
            return -18.0, 90.0
        if storage == "fridge":
            return 4.0, 65.0
        return 28.0, 78.0

    # ---------------------------------------------------------
    # CLAMP (Safety for UI / Out-of-range inputs)
    # ---------------------------------------------------------
    @staticmethod
    def _clamp(v, lo, hi):
        try:
            x = float(v)
            return max(lo, min(x, hi))
        except Exception:
            return None

    # ---------------------------------------------------------
    # BUILD MODEL INPUT ROW
    # ---------------------------------------------------------
    def _prepare_input(self, data: dict) -> pd.DataFrame:
        row = {col: 0 for col in self.feature_columns}

        # numeric features
        try:
            row["purchase_month"] = int(data.get("purchase_month", 0) or 0)
        except Exception:
            row["purchase_month"] = 0

        try:
            row["purchase_day_of_week"] = int(data.get("purchase_day_of_week", 0) or 0)
        except Exception:
            row["purchase_day_of_week"] = 0

        try:
            row["quantity"] = float(data.get("quantity", 1) or 1)
        except Exception:
            row["quantity"] = 1.0

        used = data.get("used_before_expiry", data.get("used_before_exp", False))
        if isinstance(used, str):
            used = used.strip().lower() in ("1", "true", "yes", "y", "t")
        row["used_before_expiry"] = 1 if bool(used) else 0

        # storage one-hot
        storage = (data.get("storage_type") or "pantry").lower().strip()
        if storage not in ("fridge", "freezer", "pantry"):
            storage = "pantry"
        st_col = f"storage_{storage}"
        if st_col in row:
            row[st_col] = 1

        # category one-hot (cat_*)
        category = (data.get("item_category") or "").lower().strip()
        cat_col = f"cat_{category}"
        if cat_col in row:
            row[cat_col] = 1

        # item one-hot (food_*)
        item_name = (data.get("item_name") or "").lower().strip()
        food_col = f"food_{item_name}"
        if food_col in row:
            row[food_col] = 1

        # -------------------------------------------------
        # environment features
        # -------------------------------------------------
        temp = data.get("storage_temperature_c", None)
        hum = data.get("storage_humidity_pct", None)

        # fallback to storage defaults if not provided
        if temp is None or hum is None:
            dtemp, dhum = self._default_environment(storage)
            if temp is None:
                temp = dtemp
            if hum is None:
                hum = dhum

        # clamp (prevents unrealistic / out-of-distribution values)
        # NOTE: wide clamp here; you can also do tighter clamp in food_routes per storage type.
        temp_c = self._clamp(temp, -30.0, 40.0)
        hum_p = self._clamp(hum, 40.0, 95.0)

        if temp_c is None:
            temp_c = float(self._default_environment(storage)[0])
        if hum_p is None:
            hum_p = float(self._default_environment(storage)[1])

        if "storage_temperature_c" in row:
            row["storage_temperature_c"] = float(temp_c)

        if "storage_humidity_pct" in row:
            row["storage_humidity_pct"] = float(hum_p)

        # base expiry numeric feature
        base_days = self.get_base_expiry_days(item_name, storage)
        if "item_base_expiry_days" in row:
            row["item_base_expiry_days"] = float(base_days)

        return pd.DataFrame([row])

    # ---------------------------------------------------------
    # FINAL PREDICTION (AEIF SAFE BASELINE)
    # ---------------------------------------------------------
    def predict(self, data: dict) -> dict:
        item_name = (data.get("item_name") or "").lower().strip()
        storage = (data.get("storage_type") or "pantry").lower().strip()

        base_days = float(self.get_base_expiry_days(item_name, storage))

        if self.model:
            try:
                X = self._prepare_input(data)
                raw_pred_days = float(self.model.predict(X)[0])
            except Exception as e:
                print(f"[WARN] Prediction failed: {e}. Falling back to base_days.")
                raw_pred_days = base_days
        else:
            raw_pred_days = base_days

        # -------------------------------------------------
        # AEIF safety lower bound (60% of base)
        # -------------------------------------------------
        min_safe = 0.60 * base_days
        final_days = max(raw_pred_days, min_safe)

        # usability safety: never show 0-day expiry immediately
        final_days = max(final_days, 1.0)

        # optional upper cap if model goes crazy
        final_days = min(final_days, MAX_EXPIRY_DAYS)

        return {
            "raw_pred_days": float(raw_pred_days),
            "base_expiry_days": float(base_days),
            "min_safe_days": float(min_safe),
            "final_days_until_expiry": float(final_days),
        }