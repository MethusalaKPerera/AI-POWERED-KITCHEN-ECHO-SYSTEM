import math
from typing import Dict, List, Tuple

import pandas as pd

from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.profile_store import get_profile
from NutritionGuidance.services.intake_store import get_summary


NUMERIC_SKIP = {"age_min", "age_max", "group"}

# --------------------------------------------------------
# De-duplicate micronutrient keys (mcg vs ug)
# standardize to *_ug and merge values to prevent duplicates in API output.
# --------------------------------------------------------
CANONICAL_KEY = {
    "vitamin_a_mcg": "vitamin_a_ug",
    "vitamin_d_mcg": "vitamin_d_ug",
    "vitamin_b12_mcg": "vitamin_b12_ug",
    "folate_mcg": "folate_ug",
}


def _is_number(x) -> bool:
    try:
        if x is None:
            return False
        v = float(x)
        return math.isfinite(v)
    except Exception:
        return False


def _canonicalize_keys(d: Dict) -> Dict:
    """
    Return a new dict with mcg aliases merged into canonical *_ug keys.
    - If both alias + canonical exist, canonical wins.
    - Alias keys are removed from output.
    """
    if not isinstance(d, dict):
        return d

    out: Dict = {}

    # Copy keys, mapping aliases -> canonical
    for k, v in d.items():
        ck = CANONICAL_KEY.get(k, k)

        if ck in out:
            prev = out.get(ck)

            # Prefer numeric over non-numeric; otherwise keep first meaningful value
            if _is_number(prev):
                continue
            if _is_number(v) or (v is not None and v != ""):
                out[ck] = v
        else:
            out[ck] = v

    # If both existed originally, force canonical value to win
    for alias, ck in CANONICAL_KEY.items():
        if ck in d and alias in d:
            out[ck] = d.get(ck)

    # Remove alias keys explicitly
    for alias in CANONICAL_KEY.keys():
        out.pop(alias, None)

    return out


def _clean_numeric_dict(row: Dict) -> Dict:
    """
    Convert row values to numeric where possible, skipping non-nutrient columns.
    """
    out = {}
    for k, v in row.items():
        if k in NUMERIC_SKIP:
            continue
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        if _is_number(v):
            out[k] = float(v)
    return out


def _pick_requirement_row(req_df, age: int, group: str) -> Dict:
    """
    Find the best matching requirement row:
    - group match (case-insensitive)
    - age within [age_min, age_max]
    Fallback: closest age band for that group.
    """
    group = (group or "").strip().lower()
    if not group:
        group = "male"

    df = req_df.copy()
    df["group"] = df["group"].astype(str).str.lower()

    # perfect match: group + age band
    band = df[(df["group"] == group) & (df["age_min"] <= age) & (df["age_max"] >= age)]
    if not band.empty:
        return band.iloc[0].to_dict()

    # fallback: same group, nearest band
    same_group = df[df["group"] == group]
    if not same_group.empty:
        same_group = same_group.copy()
        same_group["dist"] = (same_group["age_min"] - age).abs()
        return same_group.sort_values("dist").iloc[0].to_dict()

    # final fallback: first row
    return df.iloc[0].to_dict()


def _apply_condition_rules(
    base_req: Dict, cond_df: pd.DataFrame, conditions: List[str]
) -> Tuple[Dict, List[Dict]]:
    """
    Applies condition rules to base requirements (if dataset exists).
    Output:
      - adjusted requirements
      - condition_notes list
    """
    req = dict(base_req)
    notes = []

    if cond_df is None or cond_df.empty or not conditions:
        return req, notes

    cond_df = cond_df.copy()
    cond_df["condition"] = cond_df["condition"].astype(str).str.strip().str.lower()

    for c in conditions:
        c_key = str(c).strip().lower()
        rows = cond_df[cond_df["condition"] == c_key]
        if rows.empty:
            continue

        for _, r in rows.iterrows():
            nutrient = str(r.get("nutrient", "")).strip()
            adj = r.get("adjustment", 0)
            note = r.get("note", "")

            if nutrient and nutrient in req and _is_number(req[nutrient]) and _is_number(adj):
                req[nutrient] = float(req[nutrient]) + float(adj)

            notes.append(
                {
                    "condition": c,
                    "nutrient": nutrient,
                    "adjustment": float(adj) if _is_number(adj) else adj,
                    "note": note,
                }
            )

    return req, notes


def _severity_from_gap(gap: float, req_value: float) -> str:
    if gap <= 0:
        return "ok"
    if not _is_number(req_value) or float(req_value) <= 0:
        return "high"

    ratio = gap / float(req_value)
    if ratio >= 0.5:
        return "high"
    if ratio >= 0.25:
        return "moderate"
    return "low"


def _pick_recommendations(food_df, gaps: Dict, requirements: Dict, limit: int = 8) -> List[Dict]:
    """
    Simple recommendation logic:
    - find foods rich in nutrients with highest positive gaps
    - rank by multi-nutrient score
    """
    if food_df is None or food_df.empty:
        return []

    # choose top lacking nutrients (exclude *_upper keys)
    gap_items = [(k, v) for k, v in gaps.items() if _is_number(v) and float(v) > 0 and not str(k).endswith("_upper")]
    gap_items.sort(key=lambda x: float(x[1]), reverse=True)
    top_keys = [k for k, _ in gap_items[:6]]

    if not top_keys:
        return []

    # score foods by how much they contribute to top gaps
    df = food_df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    score = []
    for _, row in df.iterrows():
        s = 0.0
        for k in top_keys:
            if k in row and _is_number(row[k]):
                s += float(row[k])
        score.append(s)

    df["_score"] = score
    df = df.sort_values("_score", ascending=False)

    recs = []
    for _, row in df.head(limit).iterrows():
        recs.append(
            {
                "food_id": row.get("food_id"),
                "food_name": row.get("food_name") or row.get("name"),
                **{k: row.get(k) for k in top_keys if k in row},
            }
        )
    return recs


def build_report(app, user_id: str, period: str = "monthly") -> Dict:
    """
    GET /api/nutrition/report?user_id=demo&period=monthly
    """
    user_id = (user_id or "demo").strip() or "demo"
    period = (period or "monthly").strip().lower()

    food_df, req_df, cond_df = get_datasets(app)
    if req_df is None or req_df.empty:
        raise RuntimeError("Requirements dataset is empty or not loaded.")

    profile = get_profile(app, user_id) or {}
    age = profile.get("age", 22)
    group = profile.get("group", "male")
    conditions = profile.get("conditions", []) or []

    base_row = _pick_requirement_row(req_df, int(age), str(group))

    # canonicalize base requirements dict (prevents alias keys from surviving)
    requirements_base = _canonicalize_keys(
        {
            "age_min": base_row.get("age_min"),
            "age_max": base_row.get("age_max"),
            "group": str(base_row.get("group", group)).lower(),
            **_clean_numeric_dict(base_row),
        }
    )

    requirements, condition_notes = _apply_condition_rules(requirements_base, cond_df, conditions)

    # Canonicalize requirements to avoid duplicates (mcg vs ug)
    requirements = _canonicalize_keys(requirements)

    intake_summary = get_summary(app, user_id, period)
    intake_daily = intake_summary.get("daily_average_over_period") or intake_summary.get("daily_average") or {}

    # Canonicalize intake averages too (prevents duplicates from logs)
    intake_daily = _canonicalize_keys(intake_daily)

    if isinstance(intake_summary, dict):
        if isinstance(intake_summary.get("daily_average_over_period"), dict):
            intake_summary["daily_average_over_period"] = intake_daily
        if isinstance(intake_summary.get("daily_average"), dict):
            intake_summary["daily_average"] = intake_daily

    gaps = {}
    severity = {}

    for k, req_val in requirements.items():
        if k in ("age_min", "age_max", "group"):
            continue
        if not _is_number(req_val):
            continue

        intake_val = float(intake_daily.get(k, 0) or 0)

        # Upper-limit nutrients (like sodium_upper)
        if str(k).endswith("_upper"):
            excess = intake_val - float(req_val)
            gaps[k] = round(excess, 4)
            severity[k] = "high" if excess > 0 else "ok"
            continue

        gap = float(req_val) - intake_val
        gaps[k] = round(gap, 4)
        severity[k] = _severity_from_gap(gap, float(req_val))

    # Canonicalize gaps/severity (safety: in case any alias slipped through)
    gaps = _canonicalize_keys(gaps)
    severity = _canonicalize_keys(severity)

    # recommendations: ratio-based + multi-nutrient scoring
    recommendations = _pick_recommendations(food_df, gaps, requirements, limit=8)

    return {
        "period": period,
        "profile": {
            "user_id": user_id,
            "age": age,
            "group": str(group).lower(),
            "conditions": conditions,
        },
        "requirements_base": requirements_base,
        "requirements": requirements,
        "condition_notes": condition_notes,
        "intake_summary": intake_summary,
        "gaps": gaps,
        "severity": severity,
        "recommendations": recommendations,
    }
