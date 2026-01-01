
from NutritionGuidance.services.requirement_service import pick_requirements
from NutritionGuidance.services.condition_rules import apply_condition_rules

def build_report(req_df, cond_df, profile: dict, summary: dict):
    age = int(profile.get("age") or 0)
    group = profile.get("group") or "male"
    conditions = profile.get("conditions") or []

    base_req = pick_requirements(req_df, age, group)
    adj_req, notes = apply_condition_rules(base_req, cond_df, conditions)

    avg = summary.get("daily_average", {})

    # keys to compare (daily)
    compare_keys = [
        "energy_kcal", "protein_g", "fat_g", "carbohydrate_g", "fiber_g",
        "calcium_mg", "iron_mg", "zinc_mg", "magnesium_mg", "potassium_mg",
        "vitamin_c_mg", "vitamin_a_ug", "vitamin_d_ug", "vitamin_b12_ug", "folate_ug"
    ]

    gaps = {}
    severity = {}

    for k in compare_keys:
        if k not in adj_req:
            continue

        try:
            req_val = float(adj_req[k])
        except Exception:
            continue

        try:
            got = float(avg.get(k, 0.0))
        except Exception:
            got = 0.0

        gap = req_val - got
        gaps[k] = round(gap, 4)

        if gap <= 0:
            severity[k] = "ok"
        else:
            ratio = got / req_val if req_val > 0 else 0
            if ratio >= 0.8:
                severity[k] = "low"
            elif ratio >= 0.5:
                severity[k] = "moderate"
            else:
                severity[k] = "high"

    return {
        "profile": profile,
        "requirements_base": base_req,
        "requirements": adj_req,
        "condition_notes": notes,
        "intake_summary": summary,
        "gaps": gaps,
        "severity": severity,
    }
