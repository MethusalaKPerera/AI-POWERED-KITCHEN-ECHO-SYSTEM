import os
import pandas as pd

from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# --------------------------------------------------------
# PATHS
# --------------------------------------------------------
DATA_MAIN = os.path.join(os.path.dirname(__file__), "..", "data", "food_expiry_tracker_items.csv")
DATA_BASE_EXPIRY = os.path.join(os.path.dirname(__file__), "..", "data", "item_base_expiry_days.csv")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "expiry_model.cbm")
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "feature_columns.txt")


# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------
def infer_storage_from_onehot(row) -> str:
    """Derive storage from one-hot columns in dataset."""
    if row.get("storage_fridge", 0) == 1:
        return "fridge"
    if row.get("storage_freezer", 0) == 1:
        return "freezer"
    return "pantry"


def build_base_expiry_map(base_df: pd.DataFrame) -> dict:
    """
    Expects base_df columns:
      - item_name
      - base_fridge_days
      - base_freezer_days
      - base_pantry_days
    """
    base_df = base_df.copy()
    base_df["item_name"] = base_df["item_name"].astype(str).str.lower().str.strip()

    m = {}
    for _, r in base_df.iterrows():
        item = r["item_name"]
        m[item] = {
            "fridge": float(r.get("base_fridge_days", 7) or 7),
            "freezer": float(r.get("base_freezer_days", 30) or 30),
            "pantry": float(r.get("base_pantry_days", 7) or 7),
        }
    return m


# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------
print("📄 Loading main dataset:", DATA_MAIN)
df = pd.read_csv(DATA_MAIN)

print("📄 Loading base expiry dataset:", DATA_BASE_EXPIRY)
base_df = pd.read_csv(DATA_BASE_EXPIRY)

# Clean & standardize
df["item_name"] = df["item_name"].astype(str).str.lower().str.strip()

# Target
TARGET_COL = "days_until_expiry"
if TARGET_COL not in df.columns:
    raise ValueError(f"Missing target column '{TARGET_COL}' in dataset")

# Build base expiry map
base_map = build_base_expiry_map(base_df)

# --------------------------------------------------------
# FIX ISSUE A: compute correct base expiry days per row
# --------------------------------------------------------
def get_base_days(row):
    item = row["item_name"]
    storage = infer_storage_from_onehot(row)

    if item in base_map:
        return base_map[item].get(storage, 7.0)
    return 7.0  # fallback for unknown items

df["item_base_expiry_days"] = df.apply(get_base_days, axis=1)

# --------------------------------------------------------
# OPTIONAL: normalize booleans to int (prevents FutureWarning)
# --------------------------------------------------------
df = df.replace({True: 1, False: 0})
df = df.infer_objects(copy=False)

# --------------------------------------------------------
# Create item-name one-hot with a clean prefix: food_
# (This avoids collision with category columns like item_dairy)
# --------------------------------------------------------
item_dummies = pd.get_dummies(df["item_name"], prefix="food")
df = pd.concat([df.drop(columns=["item_name"]), item_dummies], axis=1)

# --------------------------------------------------------
# Rename category one-hots from item_* to cat_* to avoid confusion
# (Your dataset has category cols like item_dairy, item_meat, etc.)
# --------------------------------------------------------
category_cols = [c for c in df.columns if c.startswith("item_") and c not in ["item_base_expiry_days", "item_base_expiry_scaled"]]
rename_map = {c: c.replace("item_", "cat_", 1) for c in category_cols}
df = df.rename(columns=rename_map)

# If you already have item_base_expiry_scaled, keep it if you want,
# but we prefer the biologically meaningful feature:
# item_base_expiry_days
# (You can keep both; CatBoost will decide.)
# --------------------------------------------------------

# --------------------------------------------------------
# FEATURE SELECTION
# Drop obvious non-features if present
# --------------------------------------------------------
drop_cols = [
    TARGET_COL,
    "transaction_id",
    "user_id",
    "product_name",
    "purchase_date",
    "predicted_expiry_date",
    "storage_location",
    "notes",
]
drop_cols = [c for c in drop_cols if c in df.columns]

X = df.drop(columns=drop_cols)
y = df[TARGET_COL].astype(float)

# Ensure no NaNs
X = X.fillna(0)
y = y.fillna(y.median())

print("\n🧩 FINAL TRAINING FEATURES:", X.shape[1])

# --------------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------------------------
# TRAIN CATBOOST
# --------------------------------------------------------
print("\n🚀 Training CatBoost model (Item-Aware + Correct Base Expiry)...")

model = CatBoostRegressor(
    iterations=600,
    learning_rate=0.05,
    depth=8,
    loss_function="MAE",
    random_seed=42,
    verbose=100
)

model.fit(X_train, y_train, eval_set=(X_test, y_test), use_best_model=True)

# --------------------------------------------------------
# EVALUATE
# --------------------------------------------------------
pred = model.predict(X_test)
mae = mean_absolute_error(y_test, pred)
r2 = r2_score(y_test, pred)

print("\n📊 MODEL PERFORMANCE")
print(f"MAE (days): {mae:.4f}")
print(f"R² score   : {r2:.4f}")

# --------------------------------------------------------
# SAVE
# --------------------------------------------------------
model.save_model(MODEL_PATH)
print("💾 Saved model to:", MODEL_PATH)

with open(FEATURES_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(list(X.columns)))

print("📄 Saved feature_columns.txt")
