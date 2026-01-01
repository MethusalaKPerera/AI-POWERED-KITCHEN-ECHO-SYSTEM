# backend/NutritionGuidance/services/report_service.py

import math
from typing import Dict, List, Tuple

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

    # exact band
    band = req_df[
        (req_df["group"].astype(str).str.lower() == group)
        & (req_df["age_min"] <= age)
        & (req_df["age_max"] >= age)
    ]

    if not band.empty:
        return band.iloc[0].to_dict()

    # fallback: closest age band
    only_group = req_df[req_df["group"].astype(str).str.lower() == group]
    if only_group.empty:
        # last fallback: first row
        return req_df.iloc[0].to_dict()

    # choose closest by distance to band midpoint
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
        else:
            # keep non-numeric keys if they are useful (rare)
            pass
    return out


def _apply_condition_rules(base_req: Dict, cond_df, conditions: List[str]) -> Tuple[Dict, List[Dict]]:
    """
    Health_Condition_Nutrient_Adjustments.csv columns:
      condition, nutrient, rule_type, value, note

    rule_type supported:
      - multiplier: req[nutrient] *= value
      - add: req[nutrient] += value
      - set: req[nutrient] = value
      - upper_limit: req[nutrient+"_upper"] = min(existing, value) OR set if missing
    """
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

        # record notes always (even if rule can't be applied)
        notes.append({
            "condition": c,
            "nutrient": nutrient,
            "note": note or ""
        })

        if not _is_number(val):
            continue
        val = float(val)

        # Apply rule safely
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

        else:
            # unknown rule_type -> ignore but keep note
            continue

    return req, notes


def _severity_from_gap(gap: float, req_value: float) -> str:
    """
    Severity for deficiency gaps:
    - ok if gap <= 0
    else ratio = gap / req
    """
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


def _pick_recommendations(food_df, gaps: Dict, limit: int = 8) -> List[Dict]:
    """
    Pick foods to cover top nutrient gaps.
    Strategy: take top 2-3 nutrients with biggest positive gaps and rank foods by that nutrient amount.
    """
    if food_df is None or food_df.empty:
        return []

    # Choose top gap nutrients (exclude upper-limit keys)
    gap_items = [(k, float(v)) for k, v in gaps.items() if _is_number(v) and float(v) > 0 and not k.endswith("_upper")]
    gap_items.sort(key=lambda x: x[1], reverse=True)
    top_nutrients = [k for k, _ in gap_items[:3]]

    if not top_nutrients:
        return []

    # filter keywords (optional): remove spice mixes etc.
    bad_words = ["masala", "powder", "spice blend", "seasoning", "mix", "blend"]
    def ok_food_name(name: str) -> bool:
        n = (name or "").lower()
        return not any(w in n for w in bad_words)

    recs = []
    used = set()

    for nutr in top_nutrients:
        if nutr not in food_df.columns:
            continue

        tmp = food_df[["food_id", "food_name", "serving_basis", "serving_size_g", nutr]].copy()
        tmp = tmp.dropna(subset=["food_name", nutr])

        # numeric sort
        tmp[nutr] = tmp[nutr].astype(float, errors="ignore")
        tmp = tmp.sort_values(by=nutr, ascending=False)

        for _, r in tmp.head(50).iterrows():
            fid = str(r.get("food_id", "")).strip()
            fname = str(r.get("food_name", "")).strip()
            if not fname:
                continue
            key = fname.lower()

            if key in used:
                continue
            if not ok_food_name(fname):
                continue

            item = {
                "food_id": fid,
                "food_name": fname,
                "serving_basis": r.get("serving_basis", ""),
                "serving_size_g": r.get("serving_size_g", None),
                nutr: float(r.get(nutr, 0.0)),
            }

            # include a second important nutrient if exists
            for extra in ["calcium_mg", "iron_mg", "protein_g", "fiber_g", "potassium_mg", "vitamin_c_mg"]:
                if extra != nutr and extra in food_df.columns and extra in r.index and _is_number(r.get(extra)):
                    item[extra] = float(r.get(extra))
                    break

            recs.append(item)
            used.add(key)
            if len(recs) >= limit:
                return recs

    return recs[:limit]


def build_report(app, user_id: str, period: str = "monthly") -> Dict:
    """
    GET /api/nutrition/report?user_id=demo&period=monthly

    Returns:
      profile
      requirements_base
      requirements (condition adjusted)
      condition_notes
      intake_summary
      gaps
      severity
      recommendations
    """
    user_id = (user_id or "demo").strip() or "demo"
    period = (period or "monthly").strip().lower()

    # datasets
    food_df, req_df, cond_df = get_datasets(app)
    if req_df is None or req_df.empty:
        raise RuntimeError("Requirements dataset is empty or not loaded.")

    # profile
    profile = get_profile(app, user_id) or {}
    age = profile.get("age", 22)
    group = profile.get("group", "male")
    conditions = profile.get("conditions", []) or []

    # sanitize age
    try:
        age = int(age)
    except Exception:
        age = 22

    # requirements base row
    base_row = _pick_requirement_row(req_df, age, group)

    requirements_base = {
        "age_min": base_row.get("age_min"),
        "age_max": base_row.get("age_max"),
        "group": str(base_row.get("group", group)).lower(),
        **_clean_numeric_dict(base_row),
    }

    # apply condition adjustments
    requirements, condition_notes = _apply_condition_rules(requirements_base, cond_df, conditions)

    # intake summary (contains totals + daily averages)
    intake_summary = get_summary(app, user_id, period)

    # ✅ Use period-based daily average for gap calculation (realistic)
    intake_daily = intake_summary.get("daily_average_over_period") or intake_summary.get("daily_average") or {}

    # gaps + severity
    gaps = {}
    severity = {}

    for k, req_val in requirements.items():
        if k in NUMERIC_SKIP:
            continue
        if not _is_number(req_val):
            continue

        req_val = float(req_val)
        intake_val = float(intake_daily.get(k, 0.0)) if _is_number(intake_daily.get(k)) else 0.0

        # Upper limits: treat as "excess"
        if k.endswith("_upper"):
            excess = intake_val - req_val
            gaps[k] = round(excess, 4)  # >0 means exceeded
            severity[k] = "high" if excess > 0 else "ok"
            continue

        gap = req_val - intake_val
        gaps[k] = round(gap, 4)
        severity[k] = _severity_from_gap(gap, req_val)

    # recommendations based on gap nutrients
    recommendations = _pick_recommendations(food_df, gaps, limit=8)

    # final shape
    out = {
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

    return out
