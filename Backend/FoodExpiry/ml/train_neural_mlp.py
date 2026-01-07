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
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "food_expiry_tracker_items.csv")

# ✅ must match your CSV target column
TARGET_COL = "days_until_expiry"

# -----------------------------
# TRAINING CONFIG
# -----------------------------
BATCH_SIZE = 64
EPOCHS = 150
LR = 1e-3
PATIENCE = 12
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class TabularDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).view(-1, 1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class MLPRegressor(nn.Module):
    def __init__(self, in_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.25),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.20),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.15),

            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.net(x)


def main():
    print("📄 Loading dataset:", DATA_PATH)
    df = pd.read_csv(DATA_PATH)

    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found. Columns: {list(df.columns)}")

    # Booleans -> 0/1
    df = df.replace({True: 1, False: 0})

    # Drop missing target
    df = df.dropna(subset=[TARGET_COL]).copy()

    y = df[TARGET_COL].astype(float).values

    # Use only numeric columns as input
    X_df = df.drop(columns=[TARGET_COL], errors="ignore")
    X_df = X_df.select_dtypes(include=[np.number]).fillna(0)

    print("🧩 Feature count:", X_df.shape[1])
    print("📦 Dataset size :", len(X_df))

    X = X_df.values.astype(np.float32)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale (neural needs scaling)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train).astype(np.float32)
    X_test = scaler.transform(X_test).astype(np.float32)

    train_ds = TabularDataset(X_train, y_train)
    test_ds = TabularDataset(X_test, y_test)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)

    model = MLPRegressor(in_dim=X_train.shape[1]).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    loss_fn = nn.MSELoss()

    best_mae = float("inf")
    patience_left = PATIENCE

    print("🚀 Training Neural MLP on:", DEVICE)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        losses = []

        for xb, yb in train_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            pred = model(xb)
            loss = loss_fn(pred, yb)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            losses.append(loss.item())

        # Evaluate
        model.eval()
        preds = []
        targets = []
        with torch.no_grad():
            for xb, yb in test_loader:
                xb = xb.to(DEVICE)
                p = model(xb).cpu().numpy().reshape(-1)
                preds.append(p)
                targets.append(yb.numpy().reshape(-1))

        preds = np.concatenate(preds)
        targets = np.concatenate(targets)

        mae = mean_absolute_error(targets, preds)
        r2 = r2_score(targets, preds)

        print(
            f"Epoch {epoch:03d} | "
            f"train_loss={np.mean(losses):.6f} | "
            f"MAE={mae:.4f} | R²={r2:.4f}"
        )

        # Early stopping on MAE
        if mae < best_mae - 1e-5:
            best_mae = mae
            patience_left = PATIENCE
            # Save best weights (optional)
            torch.save(model.state_dict(), os.path.join(BASE_DIR, "..", "models", "expiry_mlp.pth"))
        else:
            patience_left -= 1
            if patience_left <= 0:
                print("⏹ Early stopping triggered.")
                break

    print("\n✅ BEST TEST MAE:", round(best_mae, 4))
    print("💾 Saved best model weights to: FoodExpiry/models/expiry_mlp.pth")


if __name__ == "__main__":
    main()
