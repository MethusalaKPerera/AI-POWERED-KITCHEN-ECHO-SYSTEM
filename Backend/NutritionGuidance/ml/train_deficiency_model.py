import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
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

    missing = [("food", col_food), ("energy", col_energy), ("protein", col_protein),
               ("calcium", col_calcium), ("iron", col_iron)]
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
    Your requirements CSV uses age_min and age_max.
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
        "age_min", "age_max",
        "req_energy_kcal", "req_protein_g", "req_calcium_mg", "req_iron_mg"
    ]

    out["age_min"] = pd.to_numeric(out["age_min"], errors="coerce")
    out["age_max"] = pd.to_numeric(out["age_max"], errors="coerce")

    for c in ["req_energy_kcal", "req_protein_g", "req_calcium_mg", "req_iron_mg"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out.dropna()
    out = out[out["age_max"] >= out["age_min"]]
    return out


def build_condition_multiplier_table(cond_df):
    """
    Optional. If your condition file doesn't match, we just ignore it safely.
    Supports:
      - energy_mult/protein_mult/... OR
      - energy_pct/protein_pct/... (percent change)
    """
    if cond_df is None or cond_df.empty:
        return None

    col_cond = pick_col(cond_df, ["condition", "health_condition", "name"])
    if col_cond is None:
        return None

    m_energy = pick_col(cond_df, ["energy_mult", "kcal_mult", "calories_mult"])
    m_protein = pick_col(cond_df, ["protein_mult"])
    m_calcium = pick_col(cond_df, ["calcium_mult"])
    m_iron = pick_col(cond_df, ["iron_mult"])

    p_energy = pick_col(cond_df, ["energy_pct", "kcal_pct", "calories_pct"])
    p_protein = pick_col(cond_df, ["protein_pct"])
    p_calcium = pick_col(cond_df, ["calcium_pct"])
    p_iron = pick_col(cond_df, ["iron_pct"])

    table = {}
    for _, r in cond_df.iterrows():
        name = str(r[col_cond]).strip().lower()

        e = pr = ca = ir = 1.0

        if any([m_energy, m_protein, m_calcium, m_iron]):
            if m_energy and pd.notna(r[m_energy]): e = float(r[m_energy])
            if m_protein and pd.notna(r[m_protein]): pr = float(r[m_protein])
            if m_calcium and pd.notna(r[m_calcium]): ca = float(r[m_calcium])
            if m_iron and pd.notna(r[m_iron]): ir = float(r[m_iron])
        elif any([p_energy, p_protein, p_calcium, p_iron]):
            if p_energy and pd.notna(r[p_energy]): e = 1.0 + float(r[p_energy]) / 100.0
            if p_protein and pd.notna(r[p_protein]): pr = 1.0 + float(r[p_protein]) / 100.0
            if p_calcium and pd.notna(r[p_calcium]): ca = 1.0 + float(r[p_calcium]) / 100.0
            if p_iron and pd.notna(r[p_iron]): ir = 1.0 + float(r[p_iron]) / 100.0
        else:
            # file doesn't have usable multipliers
            continue

        table[name] = {"energy": e, "protein": pr, "calcium": ca, "iron": ir}

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


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("📄 Loading datasets...")
    print("✅ RUNNING FILE:", __file__)
    food_df_raw = pd.read_csv(FOOD_PATH)
    req_df_raw = pd.read_csv(REQ_PATH)

    cond_df_raw = None
    if os.path.exists(COND_PATH):
        cond_df_raw = pd.read_csv(COND_PATH)

    food_df = normalize_food_columns(food_df_raw)
    req_df = normalize_req_columns(req_df_raw)
    cond_table = build_condition_multiplier_table(cond_df_raw)

    print("✅ Food rows:", len(food_df), " | Req  uirement rows:", len(req_df))
    if cond_table:
        print("✅ Condition rules detected:", len(cond_table))
    else:
        print("ℹ️ Condition adjustment table not detected/usable — training baseline only.")

    foods = food_df.to_dict("records")
    cond_names = list(cond_table.keys()) if cond_table else [None]

    samples = []
    labels = []

    SAMPLES_PER_GROUP = 200  # more samples = more stable classifier

    for _, rr in req_df.iterrows():
        age_min = int(rr["age_min"])
        age_max = int(rr["age_max"])

        base_req = {
            "energy": float(rr["req_energy_kcal"]),
            "protein": float(rr["req_protein_g"]),
            "calcium": float(rr["req_calcium_mg"]),
            "iron": float(rr["req_iron_mg"]),
        }

        for _ in range(SAMPLES_PER_GROUP):
            age = int(np.random.randint(age_min, age_max + 1))
            condition = np.random.choice(cond_names)

            req = base_req.copy()
            has_condition = 0
            if condition and cond_table:
                has_condition = 1
                mult = cond_table[condition]
                req["energy"] *= mult["energy"]
                req["protein"] *= mult["protein"]
                req["calcium"] *= mult["calcium"]
                req["iron"] *= mult["iron"]

            # simulate daily intake from real foods
            n_items = np.random.randint(3, 9)

            total_energy = total_protein = total_calcium = total_iron = 0.0

            for _k in range(n_items):
                f = foods[np.random.randint(0, len(foods))]
                grams = float(np.random.choice([50, 75, 100, 150, 200, 250, 300]))
                factor = grams / 100.0

                total_energy += f["energy_kcal"] * factor
                total_protein += f["protein_g"] * factor
                total_calcium += f["calcium_mg"] * factor
                total_iron += f["iron_mg"] * factor

            r_energy = total_energy / max(req["energy"], 1e-6)
            r_protein = total_protein / max(req["protein"], 1e-6)
            r_calcium = total_calcium / max(req["calcium"], 1e-6)
            r_iron = total_iron / max(req["iron"], 1e-6)

            risk = label_from_ratios(r_energy, r_protein, r_calcium, r_iron)

            samples.append([
                age,
                total_energy, total_protein, total_calcium, total_iron,
                r_energy, r_protein, r_calcium, r_iron,
                has_condition
            ])
            labels.append(risk)

    X = pd.DataFrame(samples, columns=[
        "age",
        "total_energy_kcal", "total_protein_g", "total_calcium_mg", "total_iron_mg",
        "ratio_energy", "ratio_protein", "ratio_calcium", "ratio_iron",
        "has_condition"
    ])
    y = pd.Series(labels, name="risk")

    print("🧪 Training rows:", len(X))
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
    print("\n📊 Accuracy:", round(accuracy_score(y_test, pred), 4))
    print(classification_report(y_test, pred))

    joblib.dump(model, MODEL_PATH)
    print("✅ ML model trained and saved at:", MODEL_PATH)


if __name__ == "__main__":
    main()
