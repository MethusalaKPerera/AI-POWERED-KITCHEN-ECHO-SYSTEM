import os
import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# --------------------------------------------------------
# PATHS
# --------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_MAIN = os.path.join(BASE_DIR, "..", "data", "food_expiry_predictor_items.csv")
DATA_BASE_EXPIRY = os.path.join(BASE_DIR, "..", "data", "item_base_expiry_days.csv")

MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "expiry_linear_regression.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "..", "models", "feature_columns_linear_regression.txt")

TARGET_COL = "days_until_expiry"

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

    base_map = {}
    for _, r in base_df.iterrows():
        item = r["item_name"]
        base_map[item] = {
            "fridge": float(r.get("base_fridge_days", 7) or 7),
            "freezer": float(r.get("base_freezer_days", 30) or 30),
            "pantry": float(r.get("base_pantry_days", 7) or 7),
        }
    return base_map


def get_base_days(row, base_map):
    item = row["item_name"]
    storage = infer_storage_from_onehot(row)
    if item in base_map:
        return base_map[item].get(storage, 7.0)
    return 7.0

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------
print("Loading main dataset:", DATA_MAIN)
df = pd.read_csv(DATA_MAIN)

print("Loading base expiry dataset:", DATA_BASE_EXPIRY)
base_df = pd.read_csv(DATA_BASE_EXPIRY)

if "item_name" not in df.columns:
    raise ValueError("Dataset must contain 'item_name' column")

if TARGET_COL not in df.columns:
    raise ValueError(f"Missing target column '{TARGET_COL}'")

df["item_name"] = df["item_name"].astype(str).str.lower().str.strip()

base_map = build_base_expiry_map(base_df)

# --------------------------------------------------------
# ADD BASE EXPIRY FEATURE
# --------------------------------------------------------
df["item_base_expiry_days"] = df.apply(lambda row: get_base_days(row, base_map), axis=1)

# --------------------------------------------------------
# NORMALIZE BOOLEANS
# --------------------------------------------------------
df = df.replace({True: 1, False: 0})
df = df.infer_objects(copy=False)

# --------------------------------------------------------
# ITEM NAME ONE-HOT
# --------------------------------------------------------
item_dummies = pd.get_dummies(df["item_name"], prefix="food")
df = pd.concat([df.drop(columns=["item_name"]), item_dummies], axis=1)

# --------------------------------------------------------
# RENAME CATEGORY ONE-HOTS
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

print("\nFinal training features:", X.shape[1])
print(
    "Includes env features?:",
    "storage_temperature_c" in X.columns and "storage_humidity_pct" in X.columns
)

# --------------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------------------------
# TRAIN LINEAR REGRESSION
# --------------------------------------------------------
print("\nTraining Linear Regression model...")

model = LinearRegression()
model.fit(X_train, y_train)

# --------------------------------------------------------
# EVALUATION
# --------------------------------------------------------
pred = model.predict(X_test)
mae = mean_absolute_error(y_test, pred)
r2 = r2_score(y_test, pred)

print("\nLINEAR REGRESSION MODEL PERFORMANCE")
print(f"MAE (days): {mae:.4f}")
print(f"R² score   : {r2:.4f}")

# --------------------------------------------------------
# SAVE MODEL + FEATURES
# --------------------------------------------------------
joblib.dump(model, MODEL_PATH)
print("Saved model to:", MODEL_PATH)

with open(FEATURES_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(list(X.columns)))

print("Saved feature_columns_linear_regression.txt")