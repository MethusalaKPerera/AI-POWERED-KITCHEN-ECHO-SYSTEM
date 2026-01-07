
from datetime import date, timedelta

from NutritionGuidance.services.dataset_loader import get_datasets
from NutritionGuidance.services.profile_store import get_profile
from NutritionGuidance.services.intake_store import get_summary
from NutritionGuidance.services.requirement_service import pick_requirements
from NutritionGuidance.services.condition_rules import apply_condition_rules
from NutritionGuidance.services.ml_risk_service import predict_risk

TRAINED_KEYS = ["energy_kcal", "protein_g", "calcium_mg", "iron_mg"]

LABELS = {
    "energy_kcal": "Energy (kcal)",
    "protein_g": "Protein (g)",
    "calcium_mg": "Calcium (mg)",
    "iron_mg": "Iron (mg)",
}


def _safe_float(x, default=0.0):
    try:
        v = float(x)
        if v != v:  # NaN check
            return default
        return v
    except Exception:
        return default


def _level_from_ratio(deficit_ratio: float) -> str:
    """
    deficit_ratio = deficit / required (0..1+)
    """
    if deficit_ratio <= 0:
        return "OK"
    if deficit_ratio >= 0.50:
        return "HIGH"
    if deficit_ratio >= 0.25:
        return "MODERATE"
    return "LOW"


def build_trained_two_week_report(app, user_id: str, period: str = "monthly", days: int = 14) -> dict:
    """
    Clean 2-week report for ONLY the 4 trained nutrients.
    - user profile
    - daily intake avg (from selected period)
    - 14-day forecast deficit + level
    - ML overall risk label
    """
    user_id = (user_id or "demo").strip() or "demo"
    period = (period or "monthly").strip().lower()

    # datasets
    _, req_df, cond_df = get_datasets(app)

    # profile
    profile = get_profile(app, user_id) or {}
    try:
        age = int(profile.get("age") or 22)
    except Exception:
        age = 22

    group = (profile.get("group") or "male").strip().lower()
    conditions = profile.get("conditions") or []
    if not isinstance(conditions, list):
        conditions = []

    # intake summary for selected period
    summary = get_summary(app, user_id, period) or {}
    avg = summary.get("daily_average_over_period") or summary.get("daily_average") or {}

    # requirements row (full row), then keep only trained keys
    base_req_row = pick_requirements(req_df, age=age, group=group) or {}
    base_req = {k: _safe_float(base_req_row.get(k, 0)) for k in TRAINED_KEYS}

    # apply condition rules (if any)
    adj_req, cond_notes = apply_condition_rules(base_req, cond_df, conditions)

    # forecast window (date info only, not statistics)
    start = date.today()
    end = start + timedelta(days=days - 1)

    nutrients = []
    for k in TRAINED_KEYS:
        required_day = _safe_float(adj_req.get(k, 0))
        intake_day = _safe_float(avg.get(k, 0))

        required_total = required_day * float(days)
        intake_total = intake_day * float(days)

        deficit = max(0.0, required_total - intake_total)
        ratio = (deficit / required_total) if required_total > 0 else (1.0 if deficit > 0 else 0.0)

        nutrients.append(
            {
                "key": k,
                "label": LABELS.get(k, k),
                "required_per_day": round(required_day, 2),
                "expected_intake_per_day": round(intake_day, 2),
                "required_total_14d": round(required_total, 2),
                "expected_total_14d": round(intake_total, 2),
                "deficit_total_14d": round(deficit, 2),
                "deficiency_level_next_14d": _level_from_ratio(ratio),
            }
        )

    # ML overall deficiency risk (uses first condition if exists)
    condition_for_ml = conditions[0] if len(conditions) > 0 else None
    ml_risk = predict_risk(age, avg, condition=condition_for_ml)

    # build clean narrative lines for UI
    lines = []
    lines.append(f"This report forecasts your next {days} days based on your recent intake pattern ({period}).")
    lines.append("If you continue the same eating pattern, these are the expected nutrient gaps and deficiency levels.")

    return {
        "type": "trained_2week_report",
        "user_id": user_id,
        "period_used": period,
        "forecast_days": int(days),
        "forecast_start": start.isoformat(),
        "forecast_end": end.isoformat(),
        "profile": {
            "user_id": user_id,
            "age": age,
            "group": group,
            "conditions": conditions,
        },
        "ml_overall_deficiency_risk": str(ml_risk),
        "condition_notes": cond_notes,  
        "nutrients": nutrients,
        "report_text": lines,
    }
