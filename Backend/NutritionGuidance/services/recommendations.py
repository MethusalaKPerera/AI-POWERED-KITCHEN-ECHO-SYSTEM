
def recommend_foods_for_gaps(food_df, gaps: dict, top_k: int = 8):
    """
    Recommend foods by top missing nutrients.
    We score foods by normalized values of the top 3 gaps.
    """
    if not gaps:
        return []

    candidates = [(k, v) for k, v in gaps.items() if isinstance(v, (int, float)) and v > 0 and k != "energy_kcal"]
    candidates.sort(key=lambda x: x[1], reverse=True)
    top_nutrients = [k for k, _ in candidates[:3]]
    if not top_nutrients:
        return []

    df = food_df.copy()

    score = None
    for n in top_nutrients:
        if n not in df.columns:
            continue
        col = df[n].fillna(0).astype(float)
        mx = float(col.max()) if len(col) else 0.0
        if mx <= 0:
            continue
        s = col / mx
        score = s if score is None else (score + s)

    if score is None:
        return []

    df["_score"] = score

    cols = ["food_name"]
    if "food_id" in df.columns:
        cols = ["food_id"] + cols
    for c in ["serving_basis", "serving_size_g"]:
        if c in df.columns:
            cols.append(c)
    cols += [n for n in top_nutrients if n in df.columns]

    out = df.sort_values("_score", ascending=False).head(top_k)[cols]
    return out.to_dict(orient="records")
