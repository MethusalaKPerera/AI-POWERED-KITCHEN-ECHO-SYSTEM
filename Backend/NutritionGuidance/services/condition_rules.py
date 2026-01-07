def apply_condition_rules(base_req: dict, cond_df, conditions: list):
    """
    Applies rule_type to base requirements.

    Your CSV columns:
      condition, nutrient, rule_type, value, note

    Supported rule_type:
      - multiplier  (req *= value)
      - add         (req += value)
      - upper_limit (req = min(req, value))  (same as set_max)
      - lower_limit (req = max(req, value))  (same as set_min)
      - set_max     (alias)
      - set_min     (alias)
    """
    req = dict(base_req)
    conditions = [str(c).strip().lower() for c in (conditions or []) if str(c).strip()]

    if cond_df is None or cond_df.empty or not conditions:
        return req, []

    cdf = cond_df.copy()

    # normalize columns
    cdf.columns = [c.strip().lower() for c in cdf.columns]

    if not {"condition", "nutrient", "rule_type", "value"}.issubset(set(cdf.columns)):
        return req, []

    cdf["condition"] = cdf["condition"].astype(str).str.strip().str.lower()
    cdf["nutrient"] = cdf["nutrient"].astype(str).str.strip()
    cdf["rule_type"] = cdf["rule_type"].astype(str).str.strip().str.lower()

    notes = []

    for cond in conditions:
        rules = cdf[cdf["condition"] == cond]
        if rules.empty:
            continue

        for _, r in rules.iterrows():
            nutrient = r.get("nutrient")
            rule_type = r.get("rule_type")
            note = r.get("note", "") if "note" in r else ""

            # only apply if nutrient exists in requirements
            if nutrient not in req:
                # still record note, because useful to show user what was ignored
                if note:
                    notes.append({
                        "condition": cond,
                        "nutrient": nutrient,
                        "note": note,
                        "rule_type": rule_type,
                        "value": r.get("value")
                    })
                continue

            try:
                base_val = float(req[nutrient])
            except Exception:
                continue

            try:
                v = float(r.get("value"))
            except Exception:
                continue

            # Apply rules
            if rule_type == "multiplier":
                req[nutrient] = base_val * v
            elif rule_type == "add":
                req[nutrient] = base_val + v
            elif rule_type in ("upper_limit", "set_max"):
                req[nutrient] = min(base_val, v)
            elif rule_type in ("lower_limit", "set_min"):
                req[nutrient] = max(base_val, v)
            else:
                # unknown rule types ignored
                continue

            if note:
                notes.append({
                    "condition": cond,
                    "nutrient": nutrient,
                    "note": note,
                    "rule_type": rule_type,
                    "value": v
                })

    return req, notes
