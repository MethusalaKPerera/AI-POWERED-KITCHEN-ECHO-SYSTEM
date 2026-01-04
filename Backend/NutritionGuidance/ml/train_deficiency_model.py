import pandas as pd
import joblib
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# -----------------------------
# Fake training data generator
# (pseudo-labeled from nutrition logic)
# -----------------------------

data = []

for age in range(18, 61):
    for energy in [800, 1200, 1600, 2000, 2400]:
        for protein in [20, 40, 60, 80]:
            for calcium in [200, 400, 800, 1200]:
                for iron in [5, 10, 15, 20]:
                    gap_score = 0

                    if energy < 1600: gap_score += 1
                    if protein < 50: gap_score += 1
                    if calcium < 800: gap_score += 1
                    if iron < 12: gap_score += 1

                    if gap_score <= 1:
                        risk = "LOW"
                    elif gap_score == 2:
                        risk = "MEDIUM"
                    else:
                        risk = "HIGH"

                    data.append([
                        age, energy, protein, calcium, iron, risk
                    ])

df = pd.DataFrame(
    data,
    columns=["age", "energy", "protein", "calcium", "iron", "risk"]
)

X = df[["age", "energy", "protein", "calcium", "iron"]]
y = df["risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = DecisionTreeClassifier(max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Save model
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "deficiency_risk_model.pkl")
joblib.dump(model, MODEL_PATH)

print(" ML model trained and saved at:", MODEL_PATH)
