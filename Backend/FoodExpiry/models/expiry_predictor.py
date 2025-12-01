import os
import pandas as pd
from datetime import datetime
from catboost import CatBoostRegressor

MODEL_PATH = os.path.join(os.path.dirname(__file__), "expiry_model.cbm")
FEATURE_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.txt")
BASE_EXPIRY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "item_base_expiry_days.csv")

MAX_MONTH = 11
MAX_WEEKDAY = 6
MAX_QTY = 10


class ExpiryPredictor:

    def __init__(self):
        print("📦 Loading CatBoost model...")
        self.model = CatBoostRegressor()
        self.model.load_model(MODEL_PATH)
        print("✅ Model loaded:", MODEL_PATH)

        # Load feature order EXACT
        with open(FEATURE_PATH, "r") as f:
            self.feature_columns = [line.strip() for line in f.readlines()]
        print("🧠 Loaded feature columns:", len(self.feature_columns))

        # ---------------------------------------------------------
        # LOAD BASE EXPIRY TABLE (fridge / freezer / pantry)
        # ---------------------------------------------------------
        base_df = pd.read_csv(BASE_EXPIRY_PATH)
        base_df["item_name"] = base_df["item_name"].str.lower().str.strip()

        # Convert to dictionary with 3 expiry types
        self.base_expiry_map = {
            row["item_name"]: {
                "fridge": row["base_fridge_days"],
                "freezer": row["base_freezer_days"],
                "pantry": row["base_pantry_days"]
            }
            for _, row in base_df.iterrows()
        }

        print(f"📘 Loaded base expiry items: {len(self.base_expiry_map)}")

    # ---------------------------------------------------------
    # SELECT CORRECT EXPIRY BASED ON STORAGE TYPE
    # ---------------------------------------------------------
    def _get_base_expiry(self, item_name: str, storage_type: str) -> float:
        if not item_name:
            return 7.0  # fallback

        item = item_name.lower().strip()
        storage = (storage_type or "pantry").lower()

        if item not in self.base_expiry_map:
            return 7.0  # unknown items fallback

        if storage not in ["fridge", "freezer", "pantry"]:
            storage = "pantry"

        return self.base_expiry_map[item][storage]

    # ---------------------------------------------------------
    # BUILD FULL FEATURE ROW
    # ---------------------------------------------------------
    def _prepare_input(self, data: dict) -> pd.DataFrame:
        row = {col: 0 for col in self.feature_columns}

        # DATE
        dt = datetime.strptime(data["purchase_date"], "%Y-%m-%d")
        row["purchase_month"] = (dt.month - 1) / MAX_MONTH
        row["purchase_day_of_week"] = dt.weekday() / MAX_WEEKDAY

        # QUANTITY NORMALIZED
        qty = float(data.get("quantity", 1))
        row["quantity"] = min(1.0, qty / MAX_QTY)

        # BOOL
        row["used_before_expiry"] = 1 if data.get("used_before_expiry") else 0

        # CATEGORY ONE-HOT
        category = (data.get("item_category") or "").lower().strip()
        cat_col = f"item_{category}"
        if cat_col in row:
            row[cat_col] = 1

        # STORAGE ONE-HOT
        storage = (data.get("storage_type") or "").lower().strip()
        if storage == "freezer": row["storage_freezer"] = 1
        elif storage == "fridge": row["storage_fridge"] = 1
        else: row["storage_pantry"] = 1

        # ITEM ONE-HOT
        item = (data.get("item_name") or "").lower().strip()
        item_col = f"item_{item}"
        if item_col in row:
            row[item_col] = 1
        else:
            print(f"⚠ WARNING: '{item}' not found in one-hot columns!")

        # -----------------------------------------------------
        # ADD NUMERICAL BASE EXPIRY (fridge/freezer/pantry)
        # -----------------------------------------------------
        row["item_base_expiry_days"] = self._get_base_expiry(
            item,
            storage
        )

        return pd.DataFrame([row], columns=self.feature_columns)

    # ---------------------------------------------------------
    # FINAL PREDICTION
    # ---------------------------------------------------------
    def predict(self, data: dict) -> dict:
        item = (data.get("item_name") or "").lower().strip()
        storage = (data.get("storage_type") or "pantry").lower()

        base_days = self._get_base_expiry(item, storage)

        features = self._prepare_input(data)
        raw = float(self.model.predict(features)[0])
        raw = max(0.0, raw)

        ml_rounded = max(1, int(round(raw)))

        # POST CORRECTION — 60% MINIMUM RULE
        final_days = max(ml_rounded, int(base_days * 0.60))

        return {
            "item_name": item,
            "storage_type": storage,
            "raw_model_output_days": raw,
            "ml_rounded_days": ml_rounded,
            "base_expiry_days": base_days,
            "final_days_until_expiry": final_days
        }

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    def validate_item(self, item_name: str) -> bool:
        if not item_name:
            return False
        return f"item_{item_name.lower().strip()}" in self.feature_columns

    def get_allowed_items(self):
        return sorted([
            col.replace("item_", "")
            for col in self.feature_columns
            if col.startswith("item_")
        ])
