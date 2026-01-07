import os
import pandas as pd
import numpy as np

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "..", "data", "food_expiry_tracker_items.csv")
OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "food_expiry_tracker_items_env.csv"
)

np.random.seed(42)  # reproducibility

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------
print("📄 Loading dataset:", INPUT_PATH)
df = pd.read_csv(INPUT_PATH)

# --------------------------------------------------
# STORAGE-BASED ENVIRONMENT RULES (Sri Lanka)
# --------------------------------------------------
def assign_environment(row):
    # Detect storage type from one-hot columns
    if row.get("storage_freezer", 0) == 1:
        temp = np.random.uniform(-20, -16)      # freezer
        humidity = np.random.uniform(85, 95)
    elif row.get("storage_fridge", 0) == 1:
        temp = np.random.uniform(3, 5)           # fridge
        humidity = np.random.uniform(60, 70)
    else:
        # pantry / ambient Sri Lankan conditions
        temp = np.random.uniform(26, 30)
        humidity = np.random.uniform(70, 85)

    return round(temp, 2), round(humidity, 2)

# --------------------------------------------------
# APPLY ENVIRONMENT ASSIGNMENT
# --------------------------------------------------
temps = []
humidities = []

for _, row in df.iterrows():
    t, h = assign_environment(row)
    temps.append(t)
    humidities.append(h)

df["storage_temperature_c"] = temps
df["storage_humidity_pct"] = humidities

# --------------------------------------------------
# SAVE NEW DATASET (original untouched)
# --------------------------------------------------
df.to_csv(OUTPUT_PATH, index=False)

print("✅ New dataset created with environmental features")
print("📄 Saved as:", OUTPUT_PATH)
print("🧩 Total columns:", df.shape[1])
