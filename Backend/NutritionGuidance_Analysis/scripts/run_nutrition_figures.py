import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# =========================================================
# PATHS
# =========================================================
# Point to Backend/data/ for nutrients + Backend/store/ for intake data
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORE_DIR = os.path.join(BASE_DIR, "store")
ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(ANALYSIS_DIR, "output_figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Use the store version (single source of truth for user intake data)
INTAKE_JSON = os.path.join(STORE_DIR, "intake_demo.json")
FOOD_CSV = os.path.join(DATA_DIR, "SL_Food_Nutrition_Master.csv")
REQ_CSV = os.path.join(DATA_DIR, "SL_Nutrient_Requirements_By_Age.csv")  # your file name

USER_ID = "demo"

# Your requirement groups: male or female
GROUP = "male"  # change to "female" if needed

# Quantity meaning: for analysis we treat 1 unit = 100g equivalent
UNIT_GRAMS_PER_SERVING = 100.0

# Which nutrients to visualize (must exist in your datasets OR be mapped via aliases below)
NUTRIENTS = {
    "energy_kcal": "Energy (kcal)",
    "protein_g": "Protein (g)",
    "calcium_mg": "Calcium (mg)",
    "iron_mg": "Iron (mg)",
}

# If your CSV uses different column names, add them here
# Example: if your food file has "energy" instead of "energy_kcal", add it under "energy_kcal".
NUTRIENT_ALIASES = {
    "energy_kcal": ["energy_kcal", "energy", "calories", "kcal"],
    "protein_g": ["protein_g", "protein", "protein_gms"],
    "calcium_mg": ["calcium_mg", "calcium", "ca_mg"],
    "iron_mg": ["iron_mg", "iron", "fe_mg"],
}


# =========================================================
# GLOBAL PLOT STYLE (clean academic style)
# =========================================================
plt.rcParams.update({
    "figure.dpi": 140,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
})


# =========================================================
# HELPERS
# =========================================================
def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def resolve_column(df: pd.DataFrame, canonical: str) -> str:
    """Return actual column name in df for the canonical nutrient using aliases."""
    cols = set(df.columns)
    for cand in NUTRIENT_ALIASES.get(canonical, [canonical]):
        if cand in cols:
            return cand
    raise ValueError(
        f"Missing column for '{canonical}'. Tried aliases {NUTRIENT_ALIASES.get(canonical, [canonical])}. "
        f"Available columns: {list(df.columns)}"
    )


def set_clean_axes(ax, xgrid=True, ygrid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if ygrid:
        ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    if xgrid:
        ax.grid(True, axis="x", linestyle="--", alpha=0.18)


def add_bar_labels(ax, fmt="{:.0f}", pad=3):
    for p in ax.patches:
        height = p.get_height()
        if np.isnan(height):
            continue
        ax.annotate(
            fmt.format(height),
            (p.get_x() + p.get_width() / 2, height),
            ha="center",
            va="bottom",
            xytext=(0, pad),
            textcoords="offset points",
            fontsize=9,
            alpha=0.9,
        )


def save_fig(fig, filename: str):
    path = os.path.join(OUT_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("[OK] Saved:", path)


# =========================================================
# LOADERS
# =========================================================
def load_intake() -> pd.DataFrame:
    with open(INTAKE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df = normalize_cols(df)

    required = ["user_id", "food_id", "food_name", "quantity", "date"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing '{c}' in intake json.")

    df = df[df["user_id"].astype(str).str.lower() == USER_ID.lower()].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0)
    df = df[df["quantity"] > 0]
    df["food_id"] = df["food_id"].astype(str).str.strip()

    return df


def load_food_master() -> pd.DataFrame:
    food = pd.read_csv(FOOD_CSV)
    food = normalize_cols(food)

    if "food_id" not in food.columns:
        if "id" in food.columns:
            food = food.rename(columns={"id": "food_id"})
        else:
            raise ValueError("Food master must contain 'food_id' (or 'id').")

    food["food_id"] = food["food_id"].astype(str).str.strip()

    # Resolve real nutrient columns using aliases
    resolved = {"food_id": "food_id"}
    for canon in NUTRIENTS.keys():
        resolved[canon] = resolve_column(food, canon)

    # Create canonical columns
    out = food[["food_id"] + [resolved[n] for n in NUTRIENTS.keys()]].copy()
    rename_map = {resolved[n]: n for n in NUTRIENTS.keys()}
    out = out.rename(columns=rename_map)
    return out


def load_requirements() -> dict:
    req = pd.read_csv(REQ_CSV)
    req = normalize_cols(req)

    # detect group column
    possible_group_cols = ["group", "sex", "gender", "category", "type"]
    group_col = None
    for c in possible_group_cols:
        if c in req.columns:
            group_col = c
            break
    if group_col is None:
        raise ValueError(f"Could not find group column. Available columns: {list(req.columns)}")

    req[group_col] = req[group_col].astype(str).str.strip().str.lower()
    row = req[req[group_col] == GROUP.lower()]
    if row.empty:
        available = req[group_col].dropna().unique()
        raise ValueError(f"Group '{GROUP}' not found in '{group_col}'. Available: {available}")
    row = row.iloc[0]

    # Resolve nutrient columns in requirements file using aliases
    req_map = {}
    for canon in NUTRIENTS.keys():
        real_col = resolve_column(req, canon)
        req_map[canon] = float(row[real_col])

    return req_map


# =========================================================
# TRANSFORM
# =========================================================
def compute_daily_intake(intake_df: pd.DataFrame, food_df: pd.DataFrame) -> pd.DataFrame:
    merged = intake_df.merge(food_df, on="food_id", how="left")

    # Warn missing mappings
    missing = merged[merged[list(NUTRIENTS.keys())[0]].isna()][["food_id", "food_name"]].drop_duplicates()
    if not missing.empty:
        print("\n[WARNING] Missing nutrient mapping for some foods (first 10):")
        print(missing.head(10).to_string(index=False))

    merged = merged.dropna(subset=list(NUTRIENTS.keys()))

    # Convert quantity -> grams (analysis assumption)
    grams = merged["quantity"] * UNIT_GRAMS_PER_SERVING
    factor = grams / 100.0  # nutrients assumed per 100g

    for n in NUTRIENTS.keys():
        merged[n] = merged[n] * factor

    daily = (
        merged.groupby(merged["date"].dt.date)[list(NUTRIENTS.keys())]
        .sum()
        .reset_index()
        .rename(columns={"date": "day"})
    )
    daily["day"] = pd.to_datetime(daily["day"])
    daily = daily.sort_values("day")
    return daily


# =========================================================
# MODELLING FIGURES (CLEAN)
# =========================================================
def fig1_weekly_trends(daily: pd.DataFrame):
    weekly = daily.set_index("day").resample("W-MON")[list(NUTRIENTS.keys())].mean()

    fig, ax = plt.subplots(figsize=(10.5, 5.2))

    for k, label in NUTRIENTS.items():
        ax.plot(weekly.index, weekly[k], marker="o", linewidth=2, markersize=4, label=label)

    ax.set_title("Figure 1: Weekly Average Nutrient Intake Trends", pad=10)
    ax.set_xlabel("Week")
    ax.set_ylabel("Average Intake (weekly mean)")
    ax.legend(ncol=2, frameon=False)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    set_clean_axes(ax, xgrid=False, ygrid=True)
    save_fig(fig, "figure_1_weekly_trends.png")


def fig2_intake_vs_requirement(daily: pd.DataFrame, req_map: dict):
    avg = daily[list(NUTRIENTS.keys())].mean().to_dict()

    labels = list(NUTRIENTS.values())
    intake_vals = [avg[k] for k in NUTRIENTS.keys()]
    req_vals = [req_map[k] for k in NUTRIENTS.keys()]

    x = np.arange(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.bar(x - width / 2, intake_vals, width=width, label="Avg Daily Intake")
    ax.bar(x + width / 2, req_vals, width=width, label="Recommended")

    ax.set_title(f"Figure 2: Average Intake vs Recommended Requirements ({GROUP.title()})", pad=10)
    ax.set_ylabel("Amount")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.legend(frameon=False)

    set_clean_axes(ax, xgrid=False, ygrid=True)
    add_bar_labels(ax, fmt="{:.0f}")

    save_fig(fig, "figure_2_intake_vs_requirement.png")


def fig3_ratio_trend_lines(daily: pd.DataFrame, req_map: dict):
    """
    Cleaner alternative:
    Shows daily adequacy ratio (intake/requirement) over time for each nutrient.
    A horizontal line at 1.0 indicates meeting the recommended requirement.
    """
    ratio = daily.copy()
    for k in NUTRIENTS.keys():
        ratio[k] = ratio[k] / max(req_map[k], 1e-9)

    # Use last 30 records to keep the plot clean
    ratio = ratio.tail(30)

    fig, ax = plt.subplots(figsize=(11.0, 5.2))

    for k, label in NUTRIENTS.items():
        ax.plot(ratio["day"], ratio[k], marker="o", linewidth=2, markersize=4, label=label)

    ax.axhline(1.0, linestyle="--", linewidth=2, alpha=0.8)
    ax.text(ratio["day"].iloc[0], 1.02, "Requirement Threshold (1.0)", fontsize=10, alpha=0.9)

    ax.axhspan(0, 1.0, alpha=0.08)

    ax.set_title("Figure 3: Daily Nutrient Adequacy Ratio Trends (Last 30 Days)", pad=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Adequacy Ratio (Intake / Requirement)")

    ymax = float(np.nanmax(ratio[list(NUTRIENTS.keys())].to_numpy()))
    ax.set_ylim(0, max(1.6, ymax + 0.2))

    ax.legend(ncol=2, frameon=False)

    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    set_clean_axes(ax, xgrid=False, ygrid=True)

    save_fig(fig, "figure_3_ratio_trends.png")


def risk_level(score: float) -> str:
    if score < 0.60:
        return "High"
    if score < 0.85:
        return "Medium"
    return "Low"


def fig4_risk_distribution(daily: pd.DataFrame, req_map: dict):
    ratio = daily.copy()
    for k in NUTRIENTS.keys():
        ratio[k] = ratio[k] / max(req_map[k], 1e-9)

    ratio["risk_score"] = ratio[list(NUTRIENTS.keys())].mean(axis=1)
    ratio["risk_level"] = ratio["risk_score"].apply(risk_level)

    order = ["Low", "Medium", "High"]
    counts = ratio["risk_level"].value_counts().reindex(order).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(8.8, 4.9))
    ax.bar(counts.index, counts.values)

    ax.set_title(f"Figure 4: Deficiency Risk Level Distribution (n = {len(ratio)} days)", pad=10)
    ax.set_xlabel("Risk Level")
    ax.set_ylabel("Number of Days")

    set_clean_axes(ax, xgrid=False, ygrid=True)
    add_bar_labels(ax, fmt="{:.0f}", pad=4)

    save_fig(fig, "figure_4_risk_distribution.png")


# =========================================================
# MAIN
# =========================================================
def main():
    print("=== NutritionGuidance Analysis Figure Generator ===")
    print("DATA_DIR:", DATA_DIR)
    print("OUT_DIR :", OUT_DIR)
    print("USER_ID :", USER_ID)
    print("GROUP   :", GROUP)

    intake = load_intake()
    food = load_food_master()
    req_map = load_requirements()

    daily = compute_daily_intake(intake, food)

    # Evidence file for report
    daily_csv = os.path.join(OUT_DIR, "daily_intake_generated.csv")
    daily.to_csv(daily_csv, index=False)
    print("[OK] Saved:", daily_csv)

    if daily.empty:
        raise ValueError("No daily nutrients computed. Check food_id mapping and nutrient columns.")

    fig1_weekly_trends(daily)
    fig2_intake_vs_requirement(daily, req_map)
    fig3_ratio_trend_lines(daily, req_map)
    fig4_risk_distribution(daily, req_map)

    print("\n[OK] DONE. Check output_figures folder for clean PNG figures.")


if __name__ == "__main__":
    main()
