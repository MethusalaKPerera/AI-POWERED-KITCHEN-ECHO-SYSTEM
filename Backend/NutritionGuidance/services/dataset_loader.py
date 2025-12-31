import os
import pandas as pd

_CACHE = {}

def _safe_read_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path)

def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip()
    return df

def _ensure_ug_mcg_aliases(df: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("vitamin_a_ug", "vitamin_a_mcg"),
        ("vitamin_d_ug", "vitamin_d_mcg"),
        ("vitamin_b12_ug", "vitamin_b12_mcg"),
        ("folate_ug", "folate_mcg"),
    ]
    for ug, mcg in pairs:
        if ug not in df.columns and mcg in df.columns:
            df[ug] = df[mcg]
        if mcg not in df.columns and ug in df.columns:
            df[mcg] = df[ug]
    return df

def get_datasets(app):
    """
    Reads 3 CSVs from backend/data/ and caches them.
    Uses app.config["DATA_DIR"] if available, otherwise backend/data/.
    """
    data_dir = app.config.get("DATA_DIR") or os.path.join(os.getcwd(), "data")
    key = ("datasets", data_dir)
    if key in _CACHE:
        return _CACHE[key]

    food_path = os.path.join(data_dir, "SL_Food_Nutrition_Master.csv")
    req_path  = os.path.join(data_dir, "SL_Nutrient_Requirements_By_Age.csv")
    cond_path = os.path.join(data_dir, "Health_Condition_Nutrient_Adjustments.csv")

    food_df = _ensure_ug_mcg_aliases(_normalize(_safe_read_csv(food_path)))
    req_df  = _ensure_ug_mcg_aliases(_normalize(_safe_read_csv(req_path)))
    cond_df = _normalize(_safe_read_csv(cond_path))

    # quick checks
    if "food_name" not in food_df.columns:
        raise ValueError("Food dataset must contain 'food_name' column")
    if "age_min" not in req_df.columns or "age_max" not in req_df.columns or "group" not in req_df.columns:
        raise ValueError("Requirements dataset must contain 'age_min', 'age_max', 'group'")
    if not {"condition", "nutrient", "rule_type", "value"}.issubset(set(cond_df.columns)):
        raise ValueError("Condition dataset must contain condition,nutrient,rule_type,value")

    _CACHE[key] = (food_df, req_df, cond_df)
    return _CACHE[key]
