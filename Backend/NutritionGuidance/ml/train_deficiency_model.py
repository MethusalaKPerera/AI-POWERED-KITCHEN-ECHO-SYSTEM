import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # backend/
DATA_DIR = os.path.join(BASE_DIR, "data")

FOOD_PATH = os.path.join(DATA_DIR, "SL_Food_Nutrition_Master.csv")
REQ_PATH = os.path.join(DATA_DIR, "SL_Nutrient_Requirements_By_Age.csv")
COND_PATH = os.path.join(DATA_DIR, "Health_Condition_Nutrient_Adjustments.csv")

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "deficiency_risk_model.pkl")

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def pick_col(df, aliases):
    """
    Finds the first matching column name in a DataFrame based on a list of aliases.
    This allows for flexible column names in user-provided CSVs.
    
    Args:
        df (pd.DataFrame): The DataFrame to search.
        aliases (list): A list of possible column name strings.
        
    Returns:
        str or None: The exact matching column name, or None if not found.
    """
    cols = {c.strip().lower(): c for c in df.columns}
    for a in aliases:
        key = a.strip().lower()
        if key in cols:
            return cols[key]
    return None


def normalize_food_columns(food_df):
    """
    Standardizes the column names of the food dataset to a consistent internal format.
    Ensures that essential columns (food, energy, protein, calcium, iron) exist
    and drops rows with missing nutritional data.
    
    Args:
        food_df (pd.DataFrame): Raw food data loaded from the CSV.
        
    Returns:
        pd.DataFrame: Cleaned and normalized food dataset.
    
    Raises:
        ValueError: If required columns cannot be found.
    """
    col_food = pick_col(food_df, ["food", "food_name", "item_name", "name"])
    col_energy = pick_col(food_df, ["energy_kcal", "energy", "kcal", "calories"])
    col_protein = pick_col(food_df, ["protein_g", "protein"])
    col_calcium = pick_col(food_df, ["calcium_mg", "calcium"])
    col_iron = pick_col(food_df, ["iron_mg", "iron"])

    missing = [
        ("food", col_food),
        ("energy", col_energy),
        ("protein", col_protein),
        ("calcium", col_calcium),
        ("iron", col_iron),
    ]
    missing = [n for n, c in missing if c is None]
    if missing:
        raise ValueError(
            f"Food master is missing required columns: {missing}\n"
            f"Available columns: {list(food_df.columns)}"
        )

    out = food_df[[col_food, col_energy, col_protein, col_calcium, col_iron]].copy()
    out.columns = ["food", "energy_kcal", "protein_g", "calcium_mg", "iron_mg"]

    for c in ["energy_kcal", "protein_g", "calcium_mg", "iron_mg"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out.dropna(subset=["energy_kcal", "protein_g", "calcium_mg", "iron_mg"])
    return out


def normalize_req_columns(req_df):
    """
    Standardizes column names for the demographic nutrient requirements dataset.
    Identifies age brackets (min/max) and required baseline nutrient levels.
    
    Args:
        req_df (pd.DataFrame): Raw requirements dataset.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with valid numeric bounds and requirements.
        
    Raises:
        ValueError: If essential age or nutrient columns are missing.
    """
    col_age_min = pick_col(req_df, ["age_min", "agemin", "min_age"])
    col_age_max = pick_col(req_df, ["age_max", "agemax", "max_age"])
    col_energy = pick_col(req_df, ["energy_kcal", "energy", "kcal", "calories"])
    col_protein = pick_col(req_df, ["protein_g", "protein"])
    col_calcium = pick_col(req_df, ["calcium_mg", "calcium"])
    col_iron = pick_col(req_df, ["iron_mg", "iron"])

    missing = [
        ("age_min", col_age_min),
        ("age_max", col_age_max),
        ("energy", col_energy),
        ("protein", col_protein),
        ("calcium", col_calcium),
        ("iron", col_iron),
    ]
    missing = [n for n, c in missing if c is None]
    if missing:
        raise ValueError(
            f"Requirements CSV is missing required columns: {missing}\n"
            f"Available columns: {list(req_df.columns)}"
        )

    out = req_df[[col_age_min, col_age_max, col_energy, col_protein, col_calcium, col_iron]].copy()
    out.columns = [
        "age_min",
        "age_max",
        "req_energy_kcal",
        "req_protein_g",
        "req_calcium_mg",
        "req_iron_mg",
    ]

    out["age_min"] = pd.to_numeric(out["age_min"], errors="coerce")
    out["age_max"] = pd.to_numeric(out["age_max"], errors="coerce")

    for c in ["req_energy_kcal", "req_protein_g", "req_calcium_mg", "req_iron_mg"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out.dropna()
    out = out[out["age_max"] >= out["age_min"]]
    return out


def normalize_cond_rules(cond_df):
    """
    Expects rule-style columns:
      condition, nutrient, rule_type, value, note(optional)
    Returns cleaned dataframe or None.
    """
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
    """
    Converts rule-style adjustments into per-condition multipliers for the 4 nutrients.

    Supported rule_type:
      - multiplier: base * value
      - add: base + value  -> multiplier approx ( (base+value)/base )
      - upper_limit: min(base, value) -> multiplier approx (min(base, value)/base)
      - lower_limit: max(base, value) -> multiplier approx (max(base, value)/base)
    """
    if cond_df_rules is None or cond_df_rules.empty:
        return None

    nutrient_map = {
        "energy_kcal": "energy",
        "protein_g": "protein",
        "calcium_mg": "calcium",
        "iron_mg": "iron",
    }

    table = {}
    for cond in sorted(set(cond_df_rules["condition"].tolist())):
        table[cond] = {"energy": 1.0, "protein": 1.0, "calcium": 1.0, "iron": 1.0}

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
        table[cond][key] *= mult
        table[cond][key] = max(0.2, min(table[cond][key], 3.0))

    return table if table else None


def label_from_ratios(r_energy, r_protein, r_calcium, r_iron):
    """
    Risk labels derived from adequacy ratio threshold rule.
    """
    below = 0
    for ratio in [r_energy, r_protein, r_calcium, r_iron]:
        if ratio < 0.80:
            below += 1

    if below == 0:
        return "LOW"
    if below <= 2:
        return "MEDIUM"
    return "HIGH"


def generate_training_data():
    """
    Generates an expansive synthetic dataset representing user profiles and their
    simulated daily food intake. It uses the real food nutritional values and the 
    baseline demographic requirements to create realistic data points.
    
    IMPORTANT: Nutrient adequacy ratios are used ONLY to assign the ground-truth
    status labels (HIGH, MEDIUM, LOW risk), and are excluded from the model features
    to prevent data leakage.
    
    Returns:
        tuple: (X, y) where X is the feature DataFrame and y is the target Series.
    """
    # Load raw CSV datasets
    food_df_raw = pd.read_csv(FOOD_PATH)
    req_df_raw = pd.read_csv(REQ_PATH)

    cond_df_raw = None
    if os.path.exists(COND_PATH):
        cond_df_raw = pd.read_csv(COND_PATH)

    food_df = normalize_food_columns(food_df_raw)
    req_df = normalize_req_columns(req_df_raw)
    cond_rules_df = normalize_cond_rules(cond_df_raw)

    foods = food_df.to_dict("records")

    samples = []
    labels = []

    SAMPLES_PER_GROUP = 200
    INTAKE_NOISE_STD = 0.06  # 6% noise
    P_NONE_CONDITION = 0.70  # ✅ ensures has_condition is not constant

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

            # choose condition (None + conditions)
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

            # simulate daily intake totals
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

            # add noise
            total_energy *= float(np.random.normal(1.0, INTAKE_NOISE_STD))
            total_protein *= float(np.random.normal(1.0, INTAKE_NOISE_STD))
            total_calcium *= float(np.random.normal(1.0, INTAKE_NOISE_STD))
            total_iron *= float(np.random.normal(1.0, INTAKE_NOISE_STD))

            # ratios for labeling only
            r_energy = total_energy / max(req_energy, 1e-6)
            r_protein = total_protein / max(req_protein, 1e-6)
            r_calcium = total_calcium / max(req_calcium, 1e-6)
            r_iron = total_iron / max(req_iron, 1e-6)

            risk = label_from_ratios(r_energy, r_protein, r_calcium, r_iron)

            # model inputs (no ratios)
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
    """
    Main orchestrator for the script.
    1. Generates synthetically simulated user intake data.
    2. Splits the data into stratified training and testing sets (80/20).
    3. Initializes and trains a balanced RandomForestClassifier.
    4. Evaluates predictions on the test set (Accuracy, Precision, Recall).
    5. Performs a 5-fold cross-validation check for reliable metrics.
    6. Serializes the trained model to a `.pkl` artifact for backend route use.
    """
    print("📄 Training deficiency risk model...")
    print("✅ RUNNING FILE:", __file__)

    # Generate simulated features (X) and risk labels (y)
    X, y = generate_training_data()
    print("🧪 Training rows:", len(X))

    # Split data to prevent overfitting; use stratify to maintain class distributions
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=10,
        random_state=RANDOM_SEED,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    acc = round(accuracy_score(y_test, pred), 4)

    print("\n📊 Accuracy:", acc)
    print(classification_report(y_test, pred))

    # cross-validation (report-ready)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
    print("📌 5-Fold CV Accuracy (mean ± std):", round(cv_scores.mean(), 4), "±", round(cv_scores.std(), 4))

    # save model
    joblib.dump(model, MODEL_PATH)
    print("✅ ML model trained and saved at:", MODEL_PATH)


if __name__ == "__main__":
    main()