import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
PRED_PATH = "food_expiry_predictor_items.csv"
BASE_PATH = "item_base_expiry_days.csv"
OUT_DIR = "results_figures"
os.makedirs(OUT_DIR, exist_ok=True)

TARGET_COL = "days_until_expiry"

# If your target is normalized 0–1, we convert to days using this scale.
# If your dataset already contains real days, the script auto-detects and uses as-is.
NORMALIZED_TO_DAYS_SCALE = 365

# -----------------------------
# LOAD
# -----------------------------
pred = pd.read_csv(PRED_PATH)
base = pd.read_csv(BASE_PATH)

# standardize item_name
pred["item_name"] = pred["item_name"].astype(str).str.lower().str.strip()
base["item_name"] = base["item_name"].astype(str).str.lower().str.strip()

# -----------------------------
# DERIVE storage_type from one-hot
# -----------------------------
def infer_storage(row):
    if row.get("storage_fridge", 0) == 1:
        return "fridge"
    if row.get("storage_freezer", 0) == 1:
        return "freezer"
    return "pantry"

pred["storage_type"] = pred.apply(infer_storage, axis=1)

# -----------------------------
# DERIVE category from one-hot item_* columns (e.g., item_dairy, item_meat ...)
# -----------------------------
cat_cols = [c for c in pred.columns if c.startswith("item_")]
# keep only category one-hots (avoid item_name column if any)
cat_cols = [c for c in cat_cols if c != "item_name"]

def infer_category(row):
    if not cat_cols:
        return "unknown"
    vals = row[cat_cols].values.astype(float)
    if np.all(vals == 0):
        return "unknown"
    return cat_cols[int(np.argmax(vals))].replace("item_", "")

pred["category"] = pred.apply(infer_category, axis=1)

# -----------------------------
# Convert target to days if normalized
# -----------------------------
if TARGET_COL not in pred.columns:
    raise ValueError(f"Missing target column: {TARGET_COL}")

target_max = float(pred[TARGET_COL].max())
if target_max <= 1.5:  # likely normalized
    pred["expiry_days"] = pred[TARGET_COL] * NORMALIZED_TO_DAYS_SCALE
    expiry_label = f"Expiry (days) [converted from normalized using scale={NORMALIZED_TO_DAYS_SCALE}]"
else:
    pred["expiry_days"] = pred[TARGET_COL]
    expiry_label = "Expiry (days)"

# -----------------------------
# Join base expiry limits
# -----------------------------
merged = pred.merge(base, on="item_name", how="left")

def base_days_for_row(r):
    st = r["storage_type"]
    if st == "fridge":
        return r.get("base_fridge_days", np.nan)
    if st == "freezer":
        return r.get("base_freezer_days", np.nan)
    return r.get("base_pantry_days", np.nan)

merged["base_days"] = merged.apply(base_days_for_row, axis=1)

# Ratio only where base_days exists
merged["expiry_base_ratio"] = merged["expiry_days"] / merged["base_days"]

# -----------------------------
# TABLES
# -----------------------------
summary_by_storage = merged.groupby("storage_type")["expiry_days"].agg(
    count="count", mean="mean", median="median", std="std", min="min", max="max"
).reset_index()

summary_by_category = merged.groupby("category")["expiry_days"].agg(
    count="count", mean="mean", median="median", std="std"
).reset_index().sort_values("count", ascending=False)

# Safety check summary: how many predicted expiry are below base (only where base exists)
valid = merged.dropna(subset=["base_days"])
below_base = (valid["expiry_days"] < valid["base_days"]).sum()
safety_check = pd.DataFrame([{
    "rows_with_base_days": len(valid),
    "below_base_count": int(below_base),
    "below_base_percent": float(below_base) / len(valid) * 100 if len(valid) else 0.0
}])

summary_by_storage.to_csv(os.path.join(OUT_DIR, "summary_by_storage.csv"), index=False)
summary_by_category.to_csv(os.path.join(OUT_DIR, "summary_by_category.csv"), index=False)
safety_check.to_csv(os.path.join(OUT_DIR, "safety_check_summary.csv"), index=False)

# -----------------------------
# FIGURE 1: Expiry vs Storage Type (boxplot)
# -----------------------------
plt.figure()
data = [merged.loc[merged["storage_type"] == s, "expiry_days"].dropna().values
        for s in ["pantry", "fridge", "freezer"]]
plt.boxplot(data, labels=["pantry", "fridge", "freezer"])
plt.title("Expiry Distribution by Storage Type")
plt.ylabel(expiry_label)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig1_expiry_by_storage.png"), dpi=200)
plt.close()

# -----------------------------
# FIGURE 2: Expiry vs Category (top 8 by count)
# -----------------------------
top_cats = summary_by_category.head(8)["category"].tolist()
plt.figure(figsize=(10, 5))
cat_data = [merged.loc[merged["category"] == c, "expiry_days"].dropna().values for c in top_cats]
plt.boxplot(cat_data, labels=top_cats, vert=True)
plt.title("Expiry Distribution by Category (Top 8)")
plt.ylabel(expiry_label)
plt.xticks(rotation=25, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig2_expiry_by_category_top8.png"), dpi=200)
plt.close()

# -----------------------------
# FIGURE 3: Temperature vs Expiry (scatter)
# -----------------------------
if "storage_temperature_c" in merged.columns:
    x = merged["storage_temperature_c"].astype(float)
    y = merged["expiry_days"].astype(float)
    mask = x.notna() & y.notna()
    corr = np.corrcoef(x[mask], y[mask])[0, 1] if mask.sum() > 2 else np.nan

    plt.figure()
    plt.scatter(x[mask], y[mask], s=10)
    plt.title(f"Temperature vs Expiry (corr={corr:.3f})" if np.isfinite(corr) else "Temperature vs Expiry")
    plt.xlabel("Storage Temperature (°C)")
    plt.ylabel(expiry_label)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig3_temp_vs_expiry.png"), dpi=200)
    plt.close()

# -----------------------------
# FIGURE 4: Humidity vs Expiry (scatter)
# -----------------------------
if "storage_humidity_pct" in merged.columns:
    x = merged["storage_humidity_pct"].astype(float)
    y = merged["expiry_days"].astype(float)
    mask = x.notna() & y.notna()
    corr = np.corrcoef(x[mask], y[mask])[0, 1] if mask.sum() > 2 else np.nan

    plt.figure()
    plt.scatter(x[mask], y[mask], s=10)
    plt.title(f"Humidity vs Expiry (corr={corr:.3f})" if np.isfinite(corr) else "Humidity vs Expiry")
    plt.xlabel("Storage Humidity (%)")
    plt.ylabel(expiry_label)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig4_humidity_vs_expiry.png"), dpi=200)
    plt.close()

# -----------------------------
# FIGURE 5: Predicted Expiry vs Base Expiry (scatter)
# -----------------------------
valid2 = merged.dropna(subset=["base_days", "expiry_days"])
if len(valid2) > 0:
    plt.figure()
    plt.scatter(valid2["base_days"], valid2["expiry_days"], s=10)
    plt.title("Predicted Expiry vs Base Expiry (Safety Reference)")
    plt.xlabel("Base Expiry (days)")
    plt.ylabel(expiry_label)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig5_pred_vs_base.png"), dpi=200)
    plt.close()

# -----------------------------
# FIGURE 6: Expiry/Base Ratio Distribution
# -----------------------------
valid3 = merged.replace([np.inf, -np.inf], np.nan).dropna(subset=["expiry_base_ratio"])
if len(valid3) > 0:
    plt.figure()
    plt.hist(valid3["expiry_base_ratio"], bins=25)
    plt.title("Distribution of Expiry/Base Ratio")
    plt.xlabel("Expiry / Base Expiry")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig6_expiry_base_ratio_hist.png"), dpi=200)
    plt.close()

print(f"✅ Saved figures + tables to: {OUT_DIR}/")
