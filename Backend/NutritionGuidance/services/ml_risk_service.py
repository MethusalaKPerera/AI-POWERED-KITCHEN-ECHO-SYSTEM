import os
import joblib
import pandas as pd

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))          # NutritionGuidance/
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))                       # backend/
DATA_DIR = os.path.join(BACKEND_DIR, "data")

REQ_PATH = os.path.join(DATA_DIR, "SL_Nutrient_Requirements_By_Age.csv")
COND_PATH = os.path.join(DATA_DIR, "Health_Condition_Nutrient_Adjustments.csv")

MODEL_PATH = os.path.join(BASE_DIR, "ml", "deficiency_risk_model.pkl")

_model = None
_req_df = None
_cond_table = None


# ------------------------------------------------------------
# Internal loaders
# ------------------------------------------------------------
def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def _load_requirements():
    """
    Loads requirement table with age_min/age_max and 4 key nutrients.
    """
    global _req_df
    if _req_df is not None:
        return _req_df

    df = pd.read_csv(REQ_PATH)

    required_cols = {"age_min", "age_max", "energy_kcal", "protein_g", "calcium_mg", "iron_mg"}
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Requirements CSV missing columns: {missing}. Found: {list(df.columns)}")

    df = df[list(required_cols)].copy()
    for c in ["age_min", "age_max", "energy_kcal", "protein_g", "calcium_mg", "iron_mg"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna()
    df = df[df["age_max"] >= df["age_min"]]

    _req_df = df
    return _req_df


def _load_condition_table():
    """
    Optional: builds nutrient multipliers by condition if the file has usable columns.
    If not usable/missing -> returns None and we run baseline.
    Supports either:
      - *_mult columns, or
      - *_pct columns (percent increase/decrease)
    """
    global _cond_table
    if _cond_table is not None:
        return _cond_table

    if not os.path.exists(COND_PATH):
        _cond_table = None
        return _cond_table

    df = pd.read_csv(COND_PATH)

    # Find a condition/name column
    cond_col = None
    for c in ["condition", "health_condition", "name"]:
        if c in df.columns:
            cond_col = c
            break
    if cond_col is None:
        _cond_table = None
        return _cond_table

    def col(*names):
        for n in names:
            if n in df.columns:
                return n
        return None

    m_energy = col("energy_mult", "kcal_mult", "calories_mult")
    m_protein = col("protein_mult")
    m_calcium = col("calcium_mult")
    m_iron = col("iron_mult")

    p_energy = col("energy_pct", "kcal_pct", "calories_pct")
    p_protein = col("protein_pct")
    p_calcium = col("calcium_pct")
    p_iron = col("iron_pct")

    table = {}
    for _, r in df.iterrows():
        name = str(r[cond_col]).strip().lower()
        if not name:
            continue

        e = pr = ca = ir = 1.0

        # multipliers
        if any([m_energy, m_protein, m_calcium, m_iron]):
            if m_energy and pd.notna(r[m_energy]): e = float(r[m_energy])
            if m_protein and pd.notna(r[m_protein]): pr = float(r[m_protein])
            if m_calcium and pd.notna(r[m_calcium]): ca = float(r[m_calcium])
            if m_iron and pd.notna(r[m_iron]): ir = float(r[m_iron])
            table[name] = {"energy": e, "protein": pr, "calcium": ca, "iron": ir}
            continue

        # percents
        if any([p_energy, p_protein, p_calcium, p_iron]):
            if p_energy and pd.notna(r[p_energy]): e = 1.0 + float(r[p_energy]) / 100.0
            if p_protein and pd.notna(r[p_protein]): pr = 1.0 + float(r[p_protein]) / 100.0
            if p_calcium and pd.notna(r[p_calcium]): ca = 1.0 + float(r[p_calcium]) / 100.0
            if p_iron and pd.notna(r[p_iron]): ir = 1.0 + float(r[p_iron]) / 100.0
            table[name] = {"energy": e, "protein": pr, "calcium": ca, "iron": ir}
            continue

    _cond_table = table if table else None
    return _cond_table


# ------------------------------------------------------------
# Requirement lookup
# ------------------------------------------------------------
def _requirements_for_age(age: int):
    """
    Returns requirement dict for the given age by selecting matching age_min/age_max row.
    """
    df = _load_requirements()
    match = df[(df["age_min"] <= age) & (age <= df["age_max"])]

    if match.empty:
        # fallback: nearest by age_min
        match = df.iloc[[int((df["age_min"] - age).abs().idxmin())]]

    row = match.iloc[0]
    return {
        "energy": float(row["energy_kcal"]),
        "protein": float(row["protein_g"]),
        "calcium": float(row["calcium_mg"]),
        "iron": float(row["iron_mg"]),
    }


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------
def predict_risk(age, avg, condition=None):
    """
    Predict deficiency risk using ML model.

    Parameters
    ----------
    age : int
    avg : dict
        daily average totals, expects keys like:
          energy_kcal, protein_g, calcium_mg, iron_mg
        (works with your daily_average_over_period output)
    condition : str | None
        optional health condition name, used only if condition adjustments exist

    Returns
    -------
    str: "LOW" | "MEDIUM" | "HIGH"
    """
    model = _load_model()

    age = int(age) if age is not None else 30
    avg = avg or {}

    total_energy = float(avg.get("energy_kcal", 0) or 0)
    total_protein = float(avg.get("protein_g", 0) or 0)
    total_calcium = float(avg.get("calcium_mg", 0) or 0)
    total_iron = float(avg.get("iron_mg", 0) or 0)

    req = _requirements_for_age(age)

    # apply condition multiplier if available
    has_condition = 0
    cond_table = _load_condition_table()
    if condition and cond_table:
        key = str(condition).strip().lower()
        if key in cond_table:
            has_condition = 1
            mult = cond_table[key]
            req["energy"] *= mult["energy"]
            req["protein"] *= mult["protein"]
            req["calcium"] *= mult["calcium"]
            req["iron"] *= mult["iron"]

    ratio_energy = total_energy / max(req["energy"], 1e-6)
    ratio_protein = total_protein / max(req["protein"], 1e-6)
    ratio_calcium = total_calcium / max(req["calcium"], 1e-6)
    ratio_iron = total_iron / max(req["iron"], 1e-6)

    import pandas as pd  # ensure this is already imported at top

    feature_names = list(model.feature_names_in_)

    row = {
        "age": age,
        "total_energy_kcal": total_energy,
        "total_protein_g": total_protein,
        "total_calcium_mg": total_calcium,
        "total_iron_mg": total_iron,
        "ratio_energy": ratio_energy,
        "ratio_protein": ratio_protein,
        "ratio_calcium": ratio_calcium,
        "ratio_iron": ratio_iron,
        "has_condition": has_condition,
    }

    X_df = pd.DataFrame([row], columns=feature_names)
    return model.predict(X_df)[0]
