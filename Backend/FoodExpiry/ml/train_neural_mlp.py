import os
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_MAIN = os.path.join(BASE_DIR, "..", "data", "food_expiry_predictor_items.csv")
DATA_BASE = os.path.join(BASE_DIR, "..", "data", "item_base_expiry_days.csv")

TARGET_COL = "days_until_expiry"

# -----------------------------
# LOAD DATA (SAME AS CATBOOST)
# -----------------------------
df = pd.read_csv(DATA_MAIN)
base_df = pd.read_csv(DATA_BASE)

df["item_name"] = df["item_name"].astype(str).str.lower().str.strip()

# --- Build base expiry map ---
base_df["item_name"] = base_df["item_name"].astype(str).str.lower().str.strip()

base_map = {}
for _, r in base_df.iterrows():
    base_map[r["item_name"]] = {
        "fridge": float(r.get("base_fridge_days", 7) or 7),
        "freezer": float(r.get("base_freezer_days", 30) or 30),
        "pantry": float(r.get("base_pantry_days", 7) or 7),
    }

def infer_storage(row):
    if row.get("storage_fridge", 0) == 1:
        return "fridge"
    if row.get("storage_freezer", 0) == 1:
        return "freezer"
    return "pantry"

def get_base_days(row):
    item = row["item_name"]
    storage = infer_storage(row)
    if item in base_map:
        return base_map[item].get(storage, 7.0)
    return 7.0

df["item_base_expiry_days"] = df.apply(get_base_days, axis=1)

# --- Boolean fix ---
df = df.replace({True: 1, False: 0})

# --- One-hot item_name ---
item_dummies = pd.get_dummies(df["item_name"], prefix="food")
df = pd.concat([df.drop(columns=["item_name"]), item_dummies], axis=1)

# --- Rename category ---
category_cols = [c for c in df.columns if c.startswith("item_")]
df = df.rename(columns={c: c.replace("item_", "cat_", 1) for c in category_cols})

# --- Feature selection ---
drop_cols = [
    TARGET_COL,
    "transaction_id",
    "user_id",
    "product_name",
    "purchase_date",
    "predicted_expiry_date",
    "storage_location",
    "notes",
]
drop_cols = [c for c in drop_cols if c in df.columns]

X = df.drop(columns=drop_cols)
y = df[TARGET_COL].astype(float)

X = X.fillna(0)
y = y.fillna(y.median())

print("🧩 Feature count:", X.shape[1])

# -----------------------------
# SPLIT + SCALE (ONLY FOR MLP)
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X.values, y.values, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -----------------------------
# TORCH DATASET
# -----------------------------
class TabDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).view(-1, 1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        return self.X[i], self.y[i]

train_loader = DataLoader(TabDataset(X_train, y_train), batch_size=64, shuffle=True)
test_loader = DataLoader(TabDataset(X_test, y_test), batch_size=64)

# -----------------------------
# MODEL
# -----------------------------
class MLP(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.net(x)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = MLP(X_train.shape[1]).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

# -----------------------------
# TRAINING
# -----------------------------
best_r2 = -999

for epoch in range(1, 101):
    model.train()
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)

        pred = model(xb)
        loss = loss_fn(pred, yb)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Evaluate
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            p = model(xb).cpu().numpy().flatten()
            preds.extend(p)
            targets.extend(yb.numpy().flatten())

    mae = mean_absolute_error(targets, preds)
    r2 = r2_score(targets, preds)

    print(f"Epoch {epoch} | MAE={mae:.4f} | R²={r2:.4f}")

    best_r2 = max(best_r2, r2)

print("\n✅ BEST R²:", round(best_r2, 4))