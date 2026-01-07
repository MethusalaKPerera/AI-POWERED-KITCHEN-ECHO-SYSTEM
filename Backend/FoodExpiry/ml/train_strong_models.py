import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import ExtraTreesRegressor

from xgboost import XGBRegressor

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "food_expiry_tracker_items.csv")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# ✅ adjust only if your target column name is different
TARGET_COL = "days_until_expiry"


def make_numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace({True: 1, False: 0})
    return df


def main():
    print("📄 Loading:", DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    df = make_numeric_df(df)

    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found in dataset columns.")

    y = df[TARGET_COL].astype(float).values

    X_df = df.drop(columns=[TARGET_COL], errors="ignore")
    X_df = X_df.select_dtypes(include=[np.number]).fillna(0)

    feature_cols = list(X_df.columns)

    print("🧩 Features:", len(feature_cols))
    print("📦 Rows    :", len(X_df))

    X_train, X_test, y_train, y_test = train_test_split(
        X_df.values, y, test_size=0.2, random_state=42
    )

    models = []

    # -------------------------
    # 1) ExtraTrees (strong baseline)
    # -------------------------
    et = ExtraTreesRegressor(
        n_estimators=1500,
        random_state=42,
        n_jobs=-1,
        max_features="sqrt",
        min_samples_split=2,
        min_samples_leaf=1,
    )
    models.append(("ExtraTrees", et))

    # -------------------------
    # 2) XGBoost (often best for tabular)
    # -------------------------
    xgb = XGBRegressor(
        n_estimators=2500,
        learning_rate=0.03,
        max_depth=8,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=1.0,
        reg_alpha=0.0,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )
    models.append(("XGBoost", xgb))

    best_name, best_r2, best_mae, best_model = None, -999, None, None

    for name, model in models:
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, pred)
        r2 = r2_score(y_test, pred)

        print(f"\n✅ {name} RESULTS")
        print(f"MAE (days): {mae:.4f}")
        print(f"R² score  : {r2:.4f}")

        if r2 > best_r2:
            best_name, best_r2, best_mae, best_model = name, r2, mae, model

    print("\n🏆 BEST MODEL:", best_name)
    print("   R² :", round(best_r2, 4))
    print("   MAE:", round(best_mae, 4))

    # Save best model + feature cols
    model_path = os.path.join(MODELS_DIR, "expiry_best_model.pkl")
    feat_path = os.path.join(MODELS_DIR, "feature_columns_best.txt")

    joblib.dump(best_model, model_path)
    with open(feat_path, "w", encoding="utf-8") as f:
        for c in feature_cols:
            f.write(c + "\n")

    print("\n💾 Saved best model:", model_path)
    print("📄 Saved feature columns:", feat_path)


if __name__ == "__main__":
    main()
