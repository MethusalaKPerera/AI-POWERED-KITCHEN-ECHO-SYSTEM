# backend/NutritionGuidance/services/food_search.py

def search_foods(food_df, q: str, limit: int = 15):
    """
    Search foods for UI autocomplete.

    - Case-insensitive "contains" search on food_name
    - Returns a small set of UI-friendly fields
    - Removes duplicates ignoring case (e.g., "Iced Tea" vs "Iced tea")

    Returns:
      [
        { food_id, food_name, serving_basis, serving_size_g },
        ...
      ]
    """
    q = (q or "").strip().lower()
    if not q:
        return []

    # contains match (case-insensitive)
    mask = food_df["food_name"].astype(str).str.lower().str.contains(q, na=False)

    # choose columns safely
    cols = []
    if "food_id" in food_df.columns:
        cols.append("food_id")

    cols.append("food_name")

    for c in ["serving_basis", "serving_size_g"]:
        if c in food_df.columns:
            cols.append(c)

    out = food_df.loc[mask, cols].copy()

    # remove duplicates ignoring case
    out["_k"] = out["food_name"].astype(str).str.lower().str.strip()
    out = out.drop_duplicates(subset=["_k"], keep="first").drop(columns=["_k"])

    # limit results
    return out.head(limit).to_dict(orient="records")
