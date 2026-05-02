import os
import pandas as pd
import joblib

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_MAIN = os.path.join(BASE_DIR, "..", "data", "food_expiry_predictor_items.csv")
DATA_BASE = os.path.join(BASE_DIR, "..", "data", "item_base_expiry_days.csv")

MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "expiry_xgboost.pkl")

TARGET_COL = "days_until_expiry"

# LOAD DATA (same pipeline)
df = pd.read_csv(DATA_MAIN)
base_df = pd.read_csv(DATA_BASE)

df["item_name"] = df["item_name"].astype(str).str.lower().str.strip()
base_df["item_name"] = base_df["item_name"].astype(str).str.lower().str.strip()

# build base map
base_map = {
    r["item_name"]: {
        "fridge": float(r.get("base_fridge_days", 7) or 7),
        "freezer": float(r.get("base_freezer_days", 30) or 30),
        "pantry": float(r.get("base_pantry_days", 7) or 7),
    }
    for _, r in base_df.iterrows()
}

def infer_storage(row):
    if row.get("storage_fridge", 0): return "fridge"
    if row.get("storage_freezer", 0): return "freezer"
    return "pantry"

def get_base(row):
    return base_map.get(row["item_name"], {}).get(infer_storage(row), 7.0)

df["item_base_expiry_days"] = df.apply(get_base, axis=1)

df = df.replace({True:1, False:0})

# one-hot
df = pd.concat([df.drop(columns=["item_name"]), pd.get_dummies(df["item_name"], prefix="food")], axis=1)

# rename
df = df.rename(columns={c: c.replace("item_","cat_",1) for c in df.columns if c.startswith("item_")})

# features
drop_cols = [TARGET_COL,"transaction_id","user_id","product_name","purchase_date","predicted_expiry_date","storage_location","notes"]
drop_cols = [c for c in drop_cols if c in df.columns]

X = df.drop(columns=drop_cols).fillna(0)
y = df[TARGET_COL].astype(float)

# split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# model
model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)

print("Training XGBoost...")
model.fit(X_train, y_train)

pred = model.predict(X_test)

print("\nXGBOOST PERFORMANCE")
print("MAE:", mean_absolute_error(y_test, pred))
print("R² :", r2_score(y_test, pred))

joblib.dump(model, MODEL_PATH)