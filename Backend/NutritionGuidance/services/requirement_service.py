
def pick_requirements(req_df, age: int, group: str):
    group = (group or "male").strip().lower()

    df = req_df.copy()
    df["group"] = df["group"].astype(str).str.strip().str.lower()

    # fallback if group not found
    gdf = df[df["group"] == group]
    if gdf.empty:
        gdf = df[df["group"] == "male"]

    age = int(age or 0)

    band = gdf[(gdf["age_min"] <= age) & (gdf["age_max"] >= age)]
    if not band.empty:
        return band.iloc[0].to_dict()

    # if no exact band, return closest last
    gdf = gdf.sort_values("age_min")
    return gdf.iloc[-1].to_dict()
