import os
import joblib
import pandas as pd
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "expiry_best_model.pkl")
FEATURE_PATH = os.path.join(os.path.dirname(__file__), "feature_columns_best.txt")
BASE_EXPIRY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "item_base_expiry_days.csv")

MAX_MONTH = 11
MAX_WEEKDAY = 6
MAX_QTY = 10


class ExpiryPredictorBest:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Missing model file: {MODEL_PATH} (train it first)")

        if not os.path.exists(FEATURE_PATH):
            raise FileNotFoundError(f"Missing feature file: {FEATURE_PATH} (train it first)")

        self.model = joblib.load(MODEL_PATH)

        with open(FEATURE_PATH, "r", encoding="utf-8") as f:
            self.feature_columns = [line.strip() for line in f.readlines() if line.strip()]

        base_df = pd.read_csv(BASE_EXPIRY_PATH)
        base_df["item_name"] = base_df["item_name"].astype(str).str.lower().str.strip()

        self.base_expiry_map = {
            row["item_name"]: {
                "fridge": float(row.get("base_fridge_days", 7)),
                "freezer": float(row.get("base_freezer_days", 7)),
                "pantry": float(row.get("base_pantry_days", 7)),
            }
            for _, row in base_df.iterrows()
        }

    def _get_base_expiry(self, item_name: str, storage_type: str) -> float:
        item = (item_name or "").lower().strip()
        storage = (storage_type or "pantry").lower().strip()

        if storage not in ["fridge", "freezer", "pantry"]:
            storage = "pantry"

        if item in self.base_expiry_map:
            return float(self.base_expiry_map[item][storage])

        return 7.0

    def _prepare_input(self, data: dict) -> pd.DataFrame:
        row = {col: 0 for col in self.feature_columns}

        dt = datetime.strptime(data["purchase_date"], "%Y-%m-%d")
        if "purchase_month" in row:
            row["purchase_month"] = (dt.month - 1) / MAX_MONTH
        if "purchase_day_of_week" in row:
            row["purchase_day_of_week"] = dt.weekday() / MAX_WEEKDAY

        qty = float(data.get("quantity", 1))
        if "quantity" in row:
            row["quantity"] = min(1.0, qty / MAX_QTY)

        if "used_before_expiry" in row:
            row["used_before_expiry"] = 1 if data.get("used_before_expiry") else 0

        category = (data.get("item_category") or "").lower().strip()
        cat_col = f"item_{category}"
        if cat_col in row:
            row[cat_col] = 1

        storage = (data.get("storage_type") or "pantry").lower().strip()
        if "storage_freezer" in row or "storage_fridge" in row or "storage_pantry" in row:
            if storage == "freezer" and "storage_freezer" in row:
                row["storage_freezer"] = 1
            elif storage == "fridge" and "storage_fridge" in row:
                row["storage_fridge"] = 1
            elif "storage_pantry" in row:
                row["storage_pantry"] = 1

        item = (data.get("item_name") or "").lower().strip()
        item_col = f"item_{item}"
        if item_col in row:
            row[item_col] = 1

        # If your training included this numeric feature
        if "item_base_expiry_days" in row:
            row["item_base_expiry_days"] = self._get_base_expiry(item, storage)

        return pd.DataFrame([row], columns=self.feature_columns)

    def predict(self, data: dict) -> dict:
        item = (data.get("item_name") or "").lower().strip()
        storage = (data.get("storage_type") or "pantry").lower().strip()
        base_days = self._get_base_expiry(item, storage)

        X = self._prepare_input(data)
        raw = float(self.model.predict(X)[0])
        raw = max(0.0, raw)
        ml_days = max(1, int(round(raw)))

        # Safety rule (your system layer)
        final_days = max(ml_days, int(base_days * 0.60))

        return {
            "item_name": item,
            "storage_type": storage,
            "raw_model_output_days": raw,
            "ml_rounded_days": ml_days,
            "base_expiry_days": base_days,
            "final_days_until_expiry": final_days
        }
