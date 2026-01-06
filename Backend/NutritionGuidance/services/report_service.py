
import math
from typing import Dict, List, Tuple

import pandas as pd

from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.profile_store import get_profile
from NutritionGuidance.services.intake_store import get_summary


NUMERIC_SKIP = {"age_min", "age_max", "group"}


def _is_number(x) -> bool:
    try:
        if x is None:
            return False
        if isinstance(x, bool):
            return False
        v = float(x)
        return math.isfinite(v)
    except Exception:
        return False


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

    band = req_df[
        (req_df["group"].astype(str).str.lower() == group)
        & (req_df["age_min"] <= age)
        & (req_df["age_max"] >= age)
    ]

    if not band.empty:
        return band.iloc[0].to_dict()

    only_group = req_df[req_df["group"].astype(str).str.lower() == group]
    if only_group.empty:
        return req_df.iloc[0].to_dict()

    def dist(row):
        mid = (float(row["age_min"]) + float(row["age_max"])) / 2.0
        return abs(mid - age)

    best = min([r for _, r in only_group.iterrows()], key=dist)
    return best.to_dict()


def _clean_numeric_dict(d: Dict) -> Dict:
    out = {}
    for k, v in d.items():
        if k in NUMERIC_SKIP:
            continue
        if _is_number(v):
            out[k] = float(v)
    return out


def _apply_condition_rules(base_req: Dict, cond_df, conditions: List[str]) -> Tuple[Dict, List[Dict]]:
    req = dict(base_req)
    notes = []

    if not conditions:
        return req, notes

    cond_set = {str(c).strip().lower() for c in conditions if str(c).strip()}
    if not cond_set:
        return req, notes

    if cond_df is None or cond_df.empty:
        return req, notes

    for _, row in cond_df.iterrows():
        c = str(row.get("condition", "")).strip().lower()
        if c not in cond_set:
            continue

        nutrient = str(row.get("nutrient", "")).strip()
        rule_type = str(row.get("rule_type", "")).strip().lower()
        val = row.get("value", None)
        note = str(row.get("note", "")).strip()

        if not nutrient:
            continue

        notes.append({
            "condition": c,
            "nutrient": nutrient,
            "note": note or ""
        })

        if not _is_number(val):
            continue
        val = float(val)

        if rule_type == "multiplier":
            if nutrient in req and _is_number(req[nutrient]):
                req[nutrient] = float(req[nutrient]) * val

        elif rule_type == "add":
            if nutrient in req and _is_number(req[nutrient]):
                req[nutrient] = float(req[nutrient]) + val
            else:
                req[nutrient] = val

        elif rule_type == "set":
            req[nutrient] = val

        elif rule_type in ("upper_limit", "upper", "limit"):
            upper_key = nutrient if nutrient.endswith("_upper") else f"{nutrient}_upper"
            if upper_key in req and _is_number(req[upper_key]):
                req[upper_key] = min(float(req[upper_key]), val)
            else:
                req[upper_key] = val

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
    Improved recommendation logic:
    - Choose top deficient nutrients by GAP RATIO (gap / requirement), not raw gap amount.
      This prevents potassium_mg from dominating just because it's in mg.
    - Score each food by how well it covers MULTIPLE deficient nutrients.
    """
    if food_df is None or getattr(food_df, "empty", True):
        return []

    # Avoid recommending spice mixes etc.
    bad_words = ["masala", "powder", "spice blend", "seasoning", "mix", "blend"]

    def ok_food_name(name: str) -> bool:
        n = (name or "").lower()
        return bool(name) and not any(w in n for w in bad_words)

    # Build candidate deficient nutrients using GAP RATIO
    candidates = []
    for k, gap in (gaps or {}).items():
        if k.endswith("_upper"):
            continue
        if not _is_number(gap) or float(gap) <= 0:
            continue
        req = requirements.get(k)
        if not _is_number(req) or float(req) <= 0:
            continue
        if k not in food_df.columns:
            continue

        ratio = float(gap) / float(req)  # <-- key fix
        candidates.append((k, float(gap), float(req), float(ratio)))

    # Sort by ratio (severity) not by raw values
    candidates.sort(key=lambda x: x[3], reverse=True)

    # Pick a set of nutrients (prefer variety, up to 6)
    top = candidates[:6]
    if not top:
        return []

    top_nutrients = [t[0] for t in top]
    weight_by_nutr = {k: max(0.15, min(ratio, 2.0)) for k, _, _, ratio in top}  # clamp weights

    # Prepare a working dataframe with required columns
    base_cols = ["food_id", "food_name", "serving_basis", "serving_size_g"]
    cols = [c for c in base_cols if c in food_df.columns] + top_nutrients
    df = food_df[cols].copy()

    # Ensure numeric
    for nutr in top_nutrients:
        df[nutr] = pd.to_numeric(df[nutr], errors="coerce")

    df = df.dropna(subset=["food_name"])
    df = df[df["food_name"].astype(str).map(ok_food_name)]

    # Compute multi-nutrient score:
    # score = Σ ( (value / requirement) * weight )
    # cap each nutrient contribution so one nutrient doesn't dominate
    def compute_score(row) -> float:
        s = 0.0
        for nutr in top_nutrients:
            v = row.get(nutr, None)
            if v is None or not _is_number(v):
                continue
            req = float(requirements.get(nutr, 1.0) or 1.0)
            if req <= 0:
                continue
            contrib = float(v) / req
            contrib = min(contrib, 1.5)  # cap
            s += contrib * float(weight_by_nutr.get(nutr, 0.2))
        return s

    df["_score"] = df.apply(compute_score, axis=1)
    df = df.sort_values(by="_score", ascending=False)

    # Deduplicate by food_name
    used = set()
    recs = []

    for _, r in df.head(200).iterrows():
        fname = str(r.get("food_name", "")).strip()
        if not fname:
            continue
        key = fname.lower()
        if key in used:
            continue

        item = {
            "food_id": str(r.get("food_id", "")).strip(),
            "food_name": fname,
            "serving_basis": r.get("serving_basis", ""),
            "serving_size_g": r.get("serving_size_g", None),
        }

        # Attach multiple nutrient values (top 4)
        nutr_values = []
        for nutr in top_nutrients:
            v = r.get(nutr, None)
            if _is_number(v) and float(v) > 0:
                nutr_values.append((nutr, float(v)))

        nutr_values.sort(key=lambda x: x[1], reverse=True)
        for nutr, v in nutr_values[:4]:
            item[nutr] = v

        recs.append(item)
        used.add(key)

        if len(recs) >= limit:
            break

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

    try:
        age = int(age)
    except Exception:
        age = 22

    base_row = _pick_requirement_row(req_df, age, group)

    requirements_base = {
        "age_min": base_row.get("age_min"),
        "age_max": base_row.get("age_max"),
        "group": str(base_row.get("group", group)).lower(),
        **_clean_numeric_dict(base_row),
    }

    requirements, condition_notes = _apply_condition_rules(requirements_base, cond_df, conditions)

    intake_summary = get_summary(app, user_id, period)
    intake_daily = intake_summary.get("daily_average_over_period") or intake_summary.get("daily_average") or {}

    gaps = {}
    severity = {}

    for k, req_val in requirements.items():
        if k in NUMERIC_SKIP:
            continue
        if not _is_number(req_val):
            continue

        req_val = float(req_val)
        intake_val = float(intake_daily.get(k, 0.0)) if _is_number(intake_daily.get(k)) else 0.0

        if k.endswith("_upper"):
            excess = intake_val - req_val
            gaps[k] = round(excess, 4)
            severity[k] = "high" if excess > 0 else "ok"
            continue

        gap = req_val - intake_val
        gaps[k] = round(gap, 4)
        severity[k] = _severity_from_gap(gap, req_val)

    # recommendations: ratio-based + multi-nutrient scoring
    recommendations = _pick_recommendations(food_df, gaps, requirements, limit=8)

    return {
        "user_id": user_id,
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
