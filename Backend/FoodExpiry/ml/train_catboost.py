import os
import pandas as pd

from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# --------------------------------------------------------
# PATHS
# --------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ USE PREDICTOR DATASET
DATA_MAIN = os.path.join(
    BASE_DIR, "..", "data", "food_expiry_predictor_items.csv"
)

DATA_BASE_EXPIRY = os.path.join(
    BASE_DIR, "..", "data", "item_base_expiry_days.csv"
)

# ✅ SAVE AS SEPARATE MODEL FOR COMPARISON
MODEL_PATH = os.path.join(
    BASE_DIR, "..", "models", "expiry_model_predictor.cbm"
)

FEATURES_PATH = os.path.join(
    BASE_DIR, "..", "models", "feature_columns_predictor.txt"
)

# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------
def infer_storage_from_onehot(row) -> str:
    if row.get("storage_fridge", 0) == 1:
        return "fridge"
    if row.get("storage_freezer", 0) == 1:
        return "freezer"
    return "pantry"


def build_base_expiry_map(base_df: pd.DataFrame) -> dict:
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
print(" Loading main dataset:", DATA_MAIN)
df = pd.read_csv(DATA_MAIN)

print(" Loading base expiry dataset:", DATA_BASE_EXPIRY)
base_df = pd.read_csv(DATA_BASE_EXPIRY)

# Standardize item_name
if "item_name" not in df.columns:
    raise ValueError("Dataset must contain 'item_name' column")

df["item_name"] = df["item_name"].astype(str).str.lower().str.strip()

# Target
TARGET_COL = "days_until_expiry"
if TARGET_COL not in df.columns:
    raise ValueError(f"Missing target column '{TARGET_COL}'")

# Build base expiry map
base_map = build_base_expiry_map(base_df)

# --------------------------------------------------------
# BASE EXPIRY DAYS PER ROW (AEIF – Issue A FIX)
# --------------------------------------------------------
def get_base_days(row):
    item = row["item_name"]
    storage = infer_storage_from_onehot(row)
    if item in base_map:
        return base_map[item].get(storage, 7.0)
    return 7.0

df["item_base_expiry_days"] = df.apply(get_base_days, axis=1)

# --------------------------------------------------------
# NORMALIZE BOOLEANS
# --------------------------------------------------------
df = df.replace({True: 1, False: 0})
df = df.infer_objects(copy=False)

# --------------------------------------------------------
# ITEM NAME ONE-HOT (food_)
# --------------------------------------------------------
item_dummies = pd.get_dummies(df["item_name"], prefix="food")
df = pd.concat([df.drop(columns=["item_name"]), item_dummies], axis=1)

# --------------------------------------------------------
# RENAME CATEGORY ONE-HOTS (item_ → cat_)
# --------------------------------------------------------
category_cols = [
    c for c in df.columns
    if c.startswith("item_")
    and c not in ["item_base_expiry_days", "item_base_expiry_scaled"]
]
rename_map = {c: c.replace("item_", "cat_", 1) for c in category_cols}
df = df.rename(columns=rename_map)

# --------------------------------------------------------
# FEATURE SELECTION
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

X = X.fillna(0)
y = y.fillna(y.median())

print("\n🧩 FINAL TRAINING FEATURES:", X.shape[1])
print(
    " Includes env features?:",
    "storage_temperature_c" in X.columns
    and "storage_humidity_pct" in X.columns
)

# --------------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------------------------
# TRAIN CATBOOST
# --------------------------------------------------------
print("\n Training CatBoost model (Extended Dataset)...")

model = CatBoostRegressor(
    iterations=600,
    learning_rate=0.04,
    depth=9,
    loss_function="MAE",
    l2_leaf_reg=3,
    random_seed=42,
    verbose=100
)

model.fit(X_train, y_train, eval_set=(X_test, y_test), use_best_model=True)

# --------------------------------------------------------
# EVALUATION
# --------------------------------------------------------
pred = model.predict(X_test)
mae = mean_absolute_error(y_test, pred)
r2 = r2_score(y_test, pred)

print("\n PREDICTOR MODEL'S PERFORMANCE")
print(f"MAE (days): {mae:.4f}")
print(f"R² score   : {r2:.4f}")

# --------------------------------------------------------
# SAVE MODEL + FEATURES
# --------------------------------------------------------
model.save_model(MODEL_PATH)
print(" Saved model to:", MODEL_PATH)

with open(FEATURES_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(list(X.columns)))

print(" Saved feature_columns_predictor.txt")
