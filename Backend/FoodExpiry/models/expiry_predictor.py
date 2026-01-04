import os
import pandas as pd
from datetime import datetime
from catboost import CatBoostRegressor


MODEL_PATH = os.path.join(os.path.dirname(__file__), "expiry_model.cbm")
FEATURE_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.txt")
BASE_EXPIRY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "item_base_expiry_days.csv")


class ExpiryPredictor:
    def __init__(self):
        # Load model
        self.model = CatBoostRegressor()
        self.model.load_model(MODEL_PATH)

        # Load feature columns
        with open(FEATURE_PATH, "r", encoding="utf-8") as f:
            self.feature_columns = [line.strip() for line in f.readlines() if line.strip()]

        # Load base expiry map
        base_df = pd.read_csv(BASE_EXPIRY_PATH)
        base_df["item_name"] = base_df["item_name"].astype(str).str.lower().str.strip()

        self.base_expiry_map = {}
        for _, r in base_df.iterrows():
            item = r["item_name"]
            self.base_expiry_map[item] = {
                "fridge": float(r.get("base_fridge_days", 7) or 7),
                "freezer": float(r.get("base_freezer_days", 30) or 30),
                "pantry": float(r.get("base_pantry_days", 7) or 7),
            }

        # Precompute allowed food items from feature columns (food_*)
        self.allowed_food_items = sorted(
            [c.replace("food_", "", 1) for c in self.feature_columns if c.startswith("food_")]
        )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    def validate_item(self, item_name: str) -> bool:
        if not item_name:
            return False
        key = f"food_{item_name.lower().strip()}"
        return key in self.feature_columns

    def get_allowed_items(self):
        return self.allowed_food_items

    # ---------------------------------------------------------
    # Base expiry lookup
    # ---------------------------------------------------------
    def get_base_expiry_days(self, item_name: str, storage_type: str) -> float:
        item = (item_name or "").lower().strip()
        storage = (storage_type or "pantry").lower().strip()

        if storage not in ("fridge", "freezer", "pantry"):
            storage = "pantry"

        if item not in self.base_expiry_map:
            return 7.0

        return float(self.base_expiry_map[item].get(storage, 7.0))

    # ---------------------------------------------------------
    # Build model feature row
    # ---------------------------------------------------------
    def _prepare_input(self, data: dict) -> pd.DataFrame:
        row = {col: 0 for col in self.feature_columns}

        # numeric / simple fields
        try:
            row["purchase_month"] = int(data.get("purchase_month", 0))
        except:
            row["purchase_month"] = 0

        try:
            row["purchase_day_of_week"] = int(data.get("purchase_day_of_week", 0))
        except:
            row["purchase_day_of_week"] = 0

        try:
            row["quantity"] = float(data.get("quantity", 0))
        except:
            row["quantity"] = 0.0

        used = data.get("used_before_expiry", data.get("used_before_exp", 0))
        row["used_before_expiry"] = 1 if str(used).lower() in ("1", "true", "yes") else 0

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

        # item-name one-hot (food_*)
        item_name = (data.get("item_name") or "").lower().strip()
        food_col = f"food_{item_name}"
        if food_col in row:
            row[food_col] = 1

        # base expiry numeric feature
        base_days = self.get_base_expiry_days(item_name, storage)
        if "item_base_expiry_days" in row:
            row["item_base_expiry_days"] = base_days

        return pd.DataFrame([row])

    # ---------------------------------------------------------
    # Predict with biological safety rule (>= 0.60 × base)
    # ---------------------------------------------------------
    def predict(self, data: dict) -> dict:
        item_name = (data.get("item_name") or "").lower().strip()
        storage = (data.get("storage_type") or "pantry").lower().strip()
        base_days = self.get_base_expiry_days(item_name, storage)

        X = self._prepare_input(data)
        raw_pred = float(self.model.predict(X)[0])

        # Step 3 biological safety rule (>= 60% of base)
        safe_min = 0.60 * base_days
        final_days = max(raw_pred, safe_min)

        return {
            "raw_pred_days": raw_pred,
            "base_expiry_days": base_days,
            "final_days_until_expiry": float(final_days),
        }
