import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

MODEL_DIR = os.path.join(BASE_DIR, "NutritionGuidance", "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

REQUIREMENTS_PATH = os.path.join(DATA_DIR, "SL_Nutrient_Requirements_By_Age.csv")

OUTPUT_MODEL_PATH = os.path.join(MODEL_DIR, "deficiency_risk_model.pkl")
OUTPUT_ENCODER_PATH = os.path.join(MODEL_DIR, "risk_label_encoder.pkl")
OUTPUT_FEATURES_PATH = os.path.join(MODEL_DIR, "deficiency_model_features.json")
OUTPUT_COMPARISON_PATH = os.path.join(MODEL_DIR, "model_comparison_results.csv")
OUTPUT_IMPORTANCE_PATH = os.path.join(MODEL_DIR, "feature_importance.csv")


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def find_column(df, possible_names):
    normalized = {
        col.lower().strip().replace(" ", "_"): col
        for col in df.columns
    }

    for name in possible_names:
        key = name.lower().strip().replace(" ", "_")
        if key in normalized:
            return normalized[key]

    return None


def safe_divide(actual, required):
    try:
        actual = float(actual or 0)
        required = float(required or 0)
        if required <= 0:
            return 0
        return actual / required
    except Exception:
        return 0


def classify_risk(row):
    ratios = [
        row["energy_ratio"],
        row["protein_ratio"],
        row["calcium_ratio"],
        row["iron_ratio"],
    ]

    deficient_count = sum(r < 0.75 for r in ratios)
    very_low_count = sum(r < 0.50 for r in ratios)
    avg_score = np.mean(ratios)

    if very_low_count >= 1 or deficient_count >= 3 or avg_score < 0.65:
        return "HIGH"
    elif deficient_count >= 1 or avg_score < 0.90:
        return "MEDIUM"
    else:
        return "LOW"


def classify_single_nutrient(ratio):
    ratio = float(ratio or 0)

    if ratio >= 0.90:
        return "LOW"
    elif ratio >= 0.70:
        return "MEDIUM"
    else:
        return "HIGH"


# ------------------------------------------------------------
# DATA GENERATION
# ------------------------------------------------------------
def generate_training_dataset(requirements_df, samples_per_group=80, random_state=42):
    rng = np.random.default_rng(random_state)

    col_age_min = find_column(requirements_df, ["age_min", "min_age", "age from"])
    col_age_max = find_column(requirements_df, ["age_max", "max_age", "age to"])
    col_gender = find_column(requirements_df, ["gender", "sex", "group"])
    col_energy = find_column(requirements_df, ["energy", "energy_kcal", "calories", "kcal"])
    col_protein = find_column(requirements_df, ["protein", "protein_g"])
    col_calcium = find_column(requirements_df, ["calcium", "calcium_mg"])
    col_iron = find_column(requirements_df, ["iron", "iron_mg"])

    missing = [
        name for name, col in [
            ("age_min", col_age_min),
            ("age_max", col_age_max),
            ("energy", col_energy),
            ("protein", col_protein),
            ("calcium", col_calcium),
            ("iron", col_iron),
        ]
        if col is None
    ]

    if missing:
        raise ValueError(f"Missing required columns in requirement dataset: {missing}")

    rows = []

    health_conditions = [
        "none",
        "diabetes",
        "hypertension",
        "anemia",
        "pregnancy",
    ]

    for _, req in requirements_df.iterrows():
        age_min = float(req[col_age_min])
        age_max = float(req[col_age_max])

        gender_value = (
            str(req[col_gender]).strip().lower()
            if col_gender
            else "general"
        )

        if gender_value.startswith("m"):
            gender_code = 1
        elif gender_value.startswith("f"):
            gender_code = 0
        else:
            gender_code = 2

        required_energy = float(req[col_energy])
        required_protein = float(req[col_protein])
        required_calcium = float(req[col_calcium])
        required_iron = float(req[col_iron])

        if age_max < age_min:
            continue

        for _ in range(samples_per_group):
            age = rng.integers(int(age_min), int(age_max) + 1)

            health_condition = rng.choice(
                health_conditions,
                p=[0.55, 0.12, 0.10, 0.13, 0.10],
            )

            risk_pattern = rng.choice(
                ["adequate", "mild", "severe"],
                p=[0.40, 0.38, 0.22],
            )

            if risk_pattern == "adequate":
                ratio_range = (0.90, 1.25)
            elif risk_pattern == "mild":
                ratio_range = (0.65, 0.95)
            else:
                ratio_range = (0.35, 0.75)

            energy_ratio = rng.uniform(*ratio_range)
            protein_ratio = rng.uniform(*ratio_range)
            calcium_ratio = rng.uniform(*ratio_range)
            iron_ratio = rng.uniform(*ratio_range)

            energy_ratio = max(0.10, energy_ratio + rng.normal(0, 0.06))
            protein_ratio = max(0.10, protein_ratio + rng.normal(0, 0.07))
            calcium_ratio = max(0.10, calcium_ratio + rng.normal(0, 0.08))
            iron_ratio = max(0.10, iron_ratio + rng.normal(0, 0.08))

            condition_flag = 0

            if health_condition == "anemia":
                iron_ratio *= rng.uniform(0.65, 0.95)
                condition_flag = 1
            elif health_condition == "pregnancy":
                calcium_ratio *= rng.uniform(0.70, 0.95)
                iron_ratio *= rng.uniform(0.70, 0.95)
                condition_flag = 1
            elif health_condition in ["diabetes", "hypertension"]:
                energy_ratio *= rng.uniform(0.80, 1.05)
                condition_flag = 1

            actual_energy = required_energy * energy_ratio
            actual_protein = required_protein * protein_ratio
            actual_calcium = required_calcium * calcium_ratio
            actual_iron = required_iron * iron_ratio

            row = {
                "age": age,
                "gender_code": gender_code,
                "condition_flag": condition_flag,

                "energy_intake": actual_energy,
                "protein_intake": actual_protein,
                "calcium_intake": actual_calcium,
                "iron_intake": actual_iron,

                "required_energy": required_energy,
                "required_protein": required_protein,
                "required_calcium": required_calcium,
                "required_iron": required_iron,

                "energy_ratio": safe_divide(actual_energy, required_energy),
                "protein_ratio": safe_divide(actual_protein, required_protein),
                "calcium_ratio": safe_divide(actual_calcium, required_calcium),
                "iron_ratio": safe_divide(actual_iron, required_iron),
            }

            row["risk_level"] = classify_risk(row)

            row["energy_risk"] = classify_single_nutrient(row["energy_ratio"])
            row["protein_risk"] = classify_single_nutrient(row["protein_ratio"])
            row["calcium_risk"] = classify_single_nutrient(row["calcium_ratio"])
            row["iron_risk"] = classify_single_nutrient(row["iron_ratio"])

            rows.append(row)

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# MODEL DEFINITIONS
# ------------------------------------------------------------
def build_models():
    return {
        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
            )),
        ]),

        "Decision Tree": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", DecisionTreeClassifier(
                random_state=42,
                max_depth=8,
                class_weight="balanced",
            )),
        ]),

        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                min_samples_split=4,
                class_weight="balanced",
            )),
        ]),

        "Gradient Boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingClassifier(
                n_estimators=180,
                learning_rate=0.05,
                max_depth=3,
                random_state=42,
            )),
        ]),
    }


# ------------------------------------------------------------
# NUTRIENT-SPECIFIC MODELS
# ------------------------------------------------------------
def train_nutrient_specific_models(training_df, features):
    nutrient_targets = {
        "energy": "energy_risk",
        "protein": "protein_risk",
        "calcium": "calcium_risk",
        "iron": "iron_risk",
    }

    X = training_df[features]

    for nutrient_name, target_col in nutrient_targets.items():
        print("\n" + "=" * 70)
        print(f"🔬 Training {nutrient_name.upper()} nutrient-specific ML model")

        y_text = training_df[target_col]

        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y_text)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )

        model = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingClassifier(
                n_estimators=180,
                learning_rate=0.05,
                max_depth=3,
                random_state=42,
            )),
        ])

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        print(f"✅ {nutrient_name.upper()} Accuracy: {accuracy:.4f}")
        print(f"✅ {nutrient_name.upper()} Weighted F1-score: {f1:.4f}")

        print("\nClassification Report:")
        print(classification_report(
            y_test,
            y_pred,
            target_names=label_encoder.classes_,
            zero_division=0,
        ))

        model_path = os.path.join(MODEL_DIR, f"{nutrient_name}_risk_model.pkl")
        encoder_path = os.path.join(MODEL_DIR, f"{nutrient_name}_risk_encoder.pkl")

        joblib.dump(model, model_path)
        joblib.dump(label_encoder, encoder_path)

        print(f"✅ Saved {nutrient_name} model at: {model_path}")
        print(f"✅ Saved {nutrient_name} encoder at: {encoder_path}")


# ------------------------------------------------------------
# MAIN TRAINING PIPELINE
# ------------------------------------------------------------
def main():
    print("📄 Training Nutritional Guidance deficiency risk model...")

    if not os.path.exists(REQUIREMENTS_PATH):
        raise FileNotFoundError(
            f"Requirement dataset not found at: {REQUIREMENTS_PATH}"
        )

    requirements_df = pd.read_csv(REQUIREMENTS_PATH)
    training_df = generate_training_dataset(requirements_df)

    print(f"🧪 Training rows generated: {len(training_df)}")
    print("📊 Target distribution:")
    print(training_df["risk_level"].value_counts())

    features = [
        "age",
        "gender_code",
        "condition_flag",

        "energy_intake",
        "protein_intake",
        "calcium_intake",
        "iron_intake",

        "required_energy",
        "required_protein",
        "required_calcium",
        "required_iron",

        "energy_ratio",
        "protein_ratio",
        "calcium_ratio",
        "iron_ratio",
    ]

    X = training_df[features]
    y_text = training_df["risk_level"]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_text)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    models = build_models()
    results = []

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    best_model_name = None
    best_model = None
    best_f1 = -1

    for model_name, model in models.items():
        print("\n" + "=" * 70)
        print(f"🔍 Training model: {model_name}")

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        cv_scores = cross_val_score(
            model,
            X,
            y,
            cv=cv,
            scoring="f1_weighted",
        )

        results.append({
            "model": model_name,
            "accuracy": round(accuracy, 4),
            "precision_weighted": round(precision, 4),
            "recall_weighted": round(recall, 4),
            "f1_weighted": round(f1, 4),
            "cv_f1_mean": round(cv_scores.mean(), 4),
            "cv_f1_std": round(cv_scores.std(), 4),
        })

        print(f"✅ Accuracy: {accuracy:.4f}")
        print(f"✅ Weighted F1-score: {f1:.4f}")
        print(f"📌 5-Fold CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        print("\nClassification Report:")
        print(classification_report(
            y_test,
            y_pred,
            target_names=label_encoder.classes_,
            zero_division=0,
        ))

        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = model_name
            best_model = model

    results_df = pd.DataFrame(results).sort_values(
        by=["f1_weighted", "cv_f1_mean"],
        ascending=False,
    )

    print("\n" + "=" * 70)
    print("📊 Model Comparison Summary:")
    print(results_df.to_string(index=False))

    print("\n🏆 Best Overall Model:", best_model_name)

    joblib.dump(best_model, OUTPUT_MODEL_PATH)
    joblib.dump(label_encoder, OUTPUT_ENCODER_PATH)

    with open(OUTPUT_FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(features, f, indent=4)

    results_df.to_csv(OUTPUT_COMPARISON_PATH, index=False)

    final_estimator = best_model.named_steps["model"]

    if hasattr(final_estimator, "feature_importances_"):
        importance_df = pd.DataFrame({
            "feature": features,
            "importance": final_estimator.feature_importances_,
        }).sort_values(by="importance", ascending=False)

        importance_df.to_csv(OUTPUT_IMPORTANCE_PATH, index=False)

        print("\n📌 Feature Importance:")
        print(importance_df.to_string(index=False))

    train_nutrient_specific_models(training_df, features)

    print("\n✅ Overall ML model saved at:", OUTPUT_MODEL_PATH)
    print("✅ Overall label encoder saved at:", OUTPUT_ENCODER_PATH)
    print("✅ Feature list saved at:", OUTPUT_FEATURES_PATH)
    print("✅ Model comparison saved at:", OUTPUT_COMPARISON_PATH)


if __name__ == "__main__":
    main()