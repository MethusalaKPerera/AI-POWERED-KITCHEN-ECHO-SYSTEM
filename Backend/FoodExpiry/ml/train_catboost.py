import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import os

# --------------------------------------------------------
# PATHS
# --------------------------------------------------------
DATA_MAIN = os.path.join(
    os.path.dirname(__file__), "..", "data", "food_expiry_tracker_items.csv"
)

DATA_BASE_EXPIRY = os.path.join(
    os.path.dirname(__file__), "..", "data", "item_base_expiry_days.csv"
)

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "expiry_model.cbm"
)

FEATURES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "feature_columns.txt"
)

MAX_EXPIRY_DAYS = 30.0


# --------------------------------------------------------
# LOAD DATASETS
# --------------------------------------------------------
print("📄 Loading main dataset:", DATA_MAIN)
df = pd.read_csv(DATA_MAIN)

print("📄 Loading base expiry dataset:", DATA_BASE_EXPIRY)
base_df = pd.read_csv(DATA_BASE_EXPIRY)

# Standard clean
df["item_name"] = df["item_name"].str.lower().str.strip()
base_df["item_name"] = base_df["item_name"].str.lower().str.strip()

# --------------------------------------------------------
# PICK CORRECT EXPIRY COLUMN BASED ON STORAGE TYPE
# --------------------------------------------------------

# If your training dataset already has `storage_type` column
def choose_expiry(row):
    item = row["item_name"]

    if item not in base_df["item_name"].values:
        return None

    matched = base_df[base_df["item_name"] == item].iloc[0]

    storage = str(row.get("storage_type", "pantry")).lower()

    if storage == "fridge":
        return matched["base_fridge_days"]
    elif storage == "freezer":
        return matched["base_freezer_days"]
    else:
        return matched["base_pantry_days"]


df["item_base_expiry_days"] = df.apply(choose_expiry, axis=1)

# If missing, use mean
df["item_base_expiry_days"] = df["item_base_expiry_days"].fillna(
    df["item_base_expiry_days"].mean()
)

df = df.replace({True: 1, False: 0})

# Build target
df["target_days"] = df["days_until_expiry"] * MAX_EXPIRY_DAYS
y = df["target_days"]

# One-hot encode item_name
item_dummies = pd.get_dummies(df["item_name"], prefix="item")
df = pd.concat([df, item_dummies], axis=1)

# Remove non-feature columns
X = df.drop(columns=[
    "days_until_expiry",
    "target_days",
    "item_name"
])

print("\n🧩 FINAL TRAINING FEATURES:", len(X.columns))

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------------
model = CatBoostRegressor(
    depth=8,
    learning_rate=0.03,
    iterations=1600,
    loss_function="RMSE",
    random_seed=42,
    l2_leaf_reg=5,
    verbose=False
)


print("\n🚀 Training CatBoost model (Item-Aware + Base Expiry Feature)...")
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print("\n📊 MODEL PERFORMANCE")
print(f"MAE (days): {mae:.4f}")
print(f"R² score   : {r2:.4f}")

# --------------------------------------------------------
# SAVE MODEL & FEATURES
# --------------------------------------------------------
model.save_model(MODEL_PATH)
print("💾 Saved model to:", MODEL_PATH)

with open(FEATURES_PATH, "w") as f:
    f.write("\n".join(list(X.columns)))

print("📄 Saved feature_columns.txt")
