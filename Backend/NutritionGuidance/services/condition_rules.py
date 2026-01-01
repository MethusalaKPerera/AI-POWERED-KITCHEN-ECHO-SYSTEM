
def apply_condition_rules(base_req: dict, cond_df, conditions: list):
    """
    Applies rule_type to base requirements.

    rule_type:
      - multiplier (e.g., 1.2)
      - add (e.g., +50)
      - upper_limit (min(current, value))
      - lower_limit (max(current, value))
    """
    req = dict(base_req)
    conditions = [str(c).strip().lower() for c in (conditions or [])]

    if cond_df is None or cond_df.empty or not conditions:
        return req, []

    cdf = cond_df.copy()
    cdf["condition"] = cdf["condition"].astype(str).str.strip().str.lower()
    cdf["nutrient"] = cdf["nutrient"].astype(str).str.strip()
    cdf["rule_type"] = cdf["rule_type"].astype(str).str.strip().str.lower()

    notes = []

    for cond in conditions:
        rules = cdf[cdf["condition"] == cond]
        if rules.empty:
            continue

        for _, r in rules.iterrows():
            nutrient = r["nutrient"]
            rule_type = r["rule_type"]
            value = r["value"]
            note = r.get("note", "")

            if note:
                notes.append({"condition": cond, "nutrient": nutrient, "note": note})

            # only apply if nutrient exists in requirements
            if nutrient not in req:
                continue

            try:
                base_val = float(req[nutrient])
            except Exception:
                continue

            try:
                v = float(value)
            except Exception:
                continue

            if rule_type == "multiplier":
                req[nutrient] = base_val * v
            elif rule_type == "add":
                req[nutrient] = base_val + v
            elif rule_type == "upper_limit":
                req[nutrient] = min(base_val, v)
            elif rule_type == "lower_limit":
                req[nutrient] = max(base_val, v)

    return req, notes
