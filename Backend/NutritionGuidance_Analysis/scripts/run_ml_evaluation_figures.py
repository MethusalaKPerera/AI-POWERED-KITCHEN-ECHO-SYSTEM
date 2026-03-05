import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# PATHS (this script is inside backend/NutritionGuidance_Analysis/scripts)
# ------------------------------------------------------------
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # backend/
DATA_DIR = os.path.join(BACKEND_DIR, "data")

FOOD_PATH = os.path.join(DATA_DIR, "SL_Food_Nutrition_Master.csv")
REQ_PATH = os.path.join(DATA_DIR, "SL_Nutrient_Requirements_By_Age.csv")
COND_PATH = os.path.join(DATA_DIR, "Health_Condition_Nutrient_Adjustments.csv")

MODEL_PATH = os.path.join(BACKEND_DIR, "NutritionGuidance", "ml", "deficiency_risk_model.pkl")

OUT_DIR = os.path.join(BACKEND_DIR, "NutritionGuidance_Analysis", "output_figures")
os.makedirs(OUT_DIR, exist_ok=True)

FIG_CM = os.path.join(OUT_DIR, "figure_5_confusion_matrix.png")
FIG_FI = os.path.join(OUT_DIR, "figure_6_feature_importance.png")

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


# ------------------------------------------------------------
# HELPERS (same logic as training, kept here so Analysis scripts are self-contained)
# ------------------------------------------------------------
def pick_col(df, aliases):
    cols = {c.strip().lower(): c for c in df.columns}
    for a in aliases:
        key = a.strip().lower()
        if key in cols:
            return cols[key]
    return None


def normalize_food_columns(food_df):
    col_food = pick_col(food_df, ["food", "food_name", "item_name", "name"])
    col_energy = pick_col(food_df, ["energy_kcal", "energy", "kcal", "calories"])
    col_protein = pick_col(food_df, ["protein_g", "protein"])
    col_calcium = pick_col(food_df, ["calcium_mg", "calcium"])
    col_iron = pick_col(food_df, ["iron_mg", "iron"])

    required = [col_food, col_energy, col_protein, col_calcium, col_iron]
    if any(c is None for c in required):
        raise ValueError(f"Food CSV missing expected nutrient columns. Found: {list(food_df.columns)}")

    out = food_df[[col_food, col_energy, col_protein, col_calcium, col_iron]].copy()
    out.columns = ["food", "energy_kcal", "protein_g", "calcium_mg", "iron_mg"]

    for c in ["energy_kcal", "protein_g", "calcium_mg", "iron_mg"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out.dropna(subset=["energy_kcal", "protein_g", "calcium_mg", "iron_mg"])
    return out


def normalize_req_columns(req_df):
    col_age_min = pick_col(req_df, ["age_min", "agemin", "min_age"])
    col_age_max = pick_col(req_df, ["age_max", "agemax", "max_age"])
    col_energy = pick_col(req_df, ["energy_kcal", "energy", "kcal", "calories"])
    col_protein = pick_col(req_df, ["protein_g", "protein"])
    col_calcium = pick_col(req_df, ["calcium_mg", "calcium"])
    col_iron = pick_col(req_df, ["iron_mg", "iron"])

    required = [col_age_min, col_age_max, col_energy, col_protein, col_calcium, col_iron]
    if any(c is None for c in required):
        raise ValueError(f"Requirement CSV missing expected columns. Found: {list(req_df.columns)}")

    out = req_df[[col_age_min, col_age_max, col_energy, col_protein, col_calcium, col_iron]].copy()
    out.columns = ["age_min", "age_max", "req_energy_kcal", "req_protein_g", "req_calcium_mg", "req_iron_mg"]

    for c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna()
    out = out[out["age_max"] >= out["age_min"]]
    return out


def normalize_cond_rules(cond_df):
    if cond_df is None or cond_df.empty:
        return None

    required = {"condition", "nutrient", "rule_type", "value"}
    cols = set([c.strip().lower() for c in cond_df.columns])
    if not required.issubset(cols):
        return None

    df = cond_df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df["condition"] = df["condition"].astype(str).str.strip().str.lower()
    df["nutrient"] = df["nutrient"].astype(str).str.strip()
    df["rule_type"] = df["rule_type"].astype(str).str.strip().str.lower()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["condition", "nutrient", "rule_type", "value"])
    return df


def build_condition_multiplier_table_from_rules(cond_df_rules, base_req_dict):
    if cond_df_rules is None or cond_df_rules.empty:
        return None

    nutrient_map = {
        "energy_kcal": "energy",
        "protein_g": "protein",
        "calcium_mg": "calcium",
        "iron_mg": "iron",
    }

    table = {cond: {"energy": 1.0, "protein": 1.0, "calcium": 1.0, "iron": 1.0}
             for cond in sorted(set(cond_df_rules["condition"].tolist()))}

    for _, r in cond_df_rules.iterrows():
        cond = r["condition"]
        nutrient = r["nutrient"]
        rule_type = r["rule_type"]
        value = float(r["value"])

        if nutrient not in nutrient_map:
            continue

        key = nutrient_map[nutrient]
        base = float(base_req_dict.get(nutrient, 0.0) or 0.0)
        if base <= 0:
            continue

        if rule_type == "multiplier":
            mult = value
        elif rule_type == "add":
            mult = (base + value) / base
        elif rule_type == "upper_limit":
            mult = min(base, value) / base
        elif rule_type == "lower_limit":
            mult = max(base, value) / base
        else:
            continue

        mult = max(0.2, min(mult, 3.0))
        table[cond][key] = max(0.2, min(table[cond][key] * mult, 3.0))

    return table if table else None


def label_from_ratios(r_energy, r_protein, r_calcium, r_iron):
    below = 0
    for ratio in [r_energy, r_protein, r_calcium, r_iron]:
        if ratio < 0.80:
            below += 1

    if below == 0:
        return "LOW"
    if below <= 2:
        return "MEDIUM"
    return "HIGH"


def generate_eval_data():
    food_df_raw = pd.read_csv(FOOD_PATH)
    req_df_raw = pd.read_csv(REQ_PATH)

    cond_df_raw = None
    if os.path.exists(COND_PATH):
        cond_df_raw = pd.read_csv(COND_PATH)

    food_df = normalize_food_columns(food_df_raw)
    req_df = normalize_req_columns(req_df_raw)
    cond_rules_df = normalize_cond_rules(cond_df_raw)

    foods = food_df.to_dict("records")

    SAMPLES_PER_GROUP = 200
    INTAKE_NOISE_STD = 0.06
    P_NONE_CONDITION = 0.70

    samples = []
    labels = []

    for _, rr in req_df.iterrows():
        age_min = int(rr["age_min"])
        age_max = int(rr["age_max"])

        base_req = {
            "energy_kcal": float(rr["req_energy_kcal"]),
            "protein_g": float(rr["req_protein_g"]),
            "calcium_mg": float(rr["req_calcium_mg"]),
            "iron_mg": float(rr["req_iron_mg"]),
        }

        cond_table = build_condition_multiplier_table_from_rules(cond_rules_df, base_req)

        for _ in range(SAMPLES_PER_GROUP):
            age = int(np.random.randint(age_min, age_max + 1))

            if cond_table:
                cond_names = [None] + list(cond_table.keys())
                p_cond_each = (1.0 - P_NONE_CONDITION) / (len(cond_names) - 1)
                cond_probs = [P_NONE_CONDITION] + [p_cond_each] * (len(cond_names) - 1)
                condition = np.random.choice(cond_names, p=cond_probs)
            else:
                condition = None

            req_energy = base_req["energy_kcal"]
            req_protein = base_req["protein_g"]
            req_calcium = base_req["calcium_mg"]
            req_iron = base_req["iron_mg"]

            has_condition = 0
            if condition and cond_table:
                has_condition = 1
                mult = cond_table[str(condition).strip().lower()]
                req_energy *= float(mult["energy"])
                req_protein *= float(mult["protein"])
                req_calcium *= float(mult["calcium"])
                req_iron *= float(mult["iron"])

            n_items = np.random.randint(3, 9)
            total_energy = total_protein = total_calcium = total_iron = 0.0

            for _k in range(n_items):
                f = foods[np.random.randint(0, len(foods))]
                grams = float(np.random.choice([50, 75, 100, 150, 200, 250, 300]))
                factor = grams / 100.0

                total_energy += float(f["energy_kcal"]) * factor
                total_protein += float(f["protein_g"]) * factor
                total_calcium += float(f["calcium_mg"]) * factor
                total_iron += float(f["iron_mg"]) * factor

            total_energy *= float(np.random.normal(1.0, INTAKE_NOISE_STD))
            total_protein *= float(np.random.normal(1.0, INTAKE_NOISE_STD))
            total_calcium *= float(np.random.normal(1.0, INTAKE_NOISE_STD))
            total_iron *= float(np.random.normal(1.0, INTAKE_NOISE_STD))

            r_energy = total_energy / max(req_energy, 1e-6)
            r_protein = total_protein / max(req_protein, 1e-6)
            r_calcium = total_calcium / max(req_calcium, 1e-6)
            r_iron = total_iron / max(req_iron, 1e-6)

            risk = label_from_ratios(r_energy, r_protein, r_calcium, r_iron)

            samples.append([
                age,
                total_energy, total_protein, total_calcium, total_iron,
                has_condition
            ])
            labels.append(risk)

    X = pd.DataFrame(samples, columns=[
        "age",
        "total_energy_kcal", "total_protein_g", "total_calcium_mg", "total_iron_mg",
        "has_condition"
    ])
    y = pd.Series(labels, name="risk")

    return X, y


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("=== ML Evaluation Figure Generator ===")
    print("MODEL_PATH:", MODEL_PATH)
    print("OUT_DIR   :", OUT_DIR)

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at: {MODEL_PATH}\n"
            f"Run: python backend/NutritionGuidance/ml/train_deficiency_model.py"
        )

    model = joblib.load(MODEL_PATH)

    # rebuild eval dataset (same seed + same generator logic)
    X, y = generate_eval_data()

    # standard split for evaluation figures
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    pred = model.predict(X_test)

    # ---- Figure 5: Confusion Matrix
    cm = confusion_matrix(y_test, pred, labels=["LOW", "MEDIUM", "HIGH"])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["LOW", "MEDIUM", "HIGH"])

    fig = plt.figure(figsize=(7.2, 5.4), dpi=150)
    ax = fig.add_subplot(111)
    disp.plot(ax=ax, values_format="d")
    ax.set_title("Figure 5: Confusion Matrix of Random Forest Classifier (Test Set)")
    fig.tight_layout()
    fig.savefig(FIG_CM, bbox_inches="tight")
    plt.close(fig)
    print("✅ Saved:", FIG_CM)

    # ---- Figure 6: Feature Importance
    feature_names = list(getattr(model, "feature_names_in_", X.columns))
    importances = pd.Series(model.feature_importances_, index=feature_names).sort_values(ascending=False)

    fig = plt.figure(figsize=(8.6, 5.0), dpi=150)
    ax = fig.add_subplot(111)
    ax.bar(importances.index, importances.values)
    ax.set_title("Figure 6: Random Forest Feature Importance")
    ax.set_xlabel("Feature")
    ax.set_ylabel("Importance")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(FIG_FI, bbox_inches="tight")
    plt.close(fig)
    print("✅ Saved:", FIG_FI)

    print("✅ Done. Now output_figures contains Figure 5 & 6.")


if __name__ == "__main__":
    main()