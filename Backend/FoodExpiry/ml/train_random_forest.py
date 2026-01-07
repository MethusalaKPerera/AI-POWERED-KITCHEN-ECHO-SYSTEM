import os
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


# --------------------------------------------------------
# PATHS
# --------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "food_expiry_tracker_items.csv")

# ✅ Adjust ONLY if your target column name is different
TARGET_COL = "days_until_expiry"


def main():
    print("📄 Loading dataset:", DATA_PATH)
    df = pd.read_csv(DATA_PATH)

    if TARGET_COL not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COL}' not found.\n"
            f"Available columns: {list(df.columns)}"
        )

    # --------------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------------
    df = df.replace({True: 1, False: 0})
    df = df.dropna(subset=[TARGET_COL])

    y = df[TARGET_COL].astype(float).values

    # Use only numeric columns for Random Forest
    X_df = df.drop(columns=[TARGET_COL], errors="ignore")
    X_df = X_df.select_dtypes(include=[np.number]).fillna(0)

    print("🧩 Feature count:", X_df.shape[1])
    print("📦 Dataset size :", len(X_df))

    # --------------------------------------------------------
    # TRAIN / TEST SPLIT
    # --------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X_df.values,
        y,
        test_size=0.2,
        random_state=42
    )

    # --------------------------------------------------------
    # RANDOM FOREST MODEL
    # --------------------------------------------------------
    model = RandomForestRegressor(
        n_estimators=1200,
        random_state=42,
        n_jobs=-1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt"
    )

    print("🚀 Training Random Forest Regressor...")
    model.fit(X_train, y_train)

    # --------------------------------------------------------
    # EVALUATION
    # --------------------------------------------------------
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print("\n📊 RANDOM FOREST PERFORMANCE")
    print("MAE (days):", round(mae, 4))
    print("R² score  :", round(r2, 4))

    print("\n✅ Random Forest experiment completed.")


if __name__ == "__main__":
    main()
