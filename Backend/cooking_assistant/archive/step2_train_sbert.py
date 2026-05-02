"""
STEP 2 (FIXED) — FINE-TUNE SENTENCE-BERT CLASSIFIER
=====================================================
Fixes applied vs the original:
  1. Learning rate: 2e-5 → 1e-3  (classifier head needs higher LR than BERT backbone)
  2. Class weights: handles imbalance (127 Curry vs 13 Beverage)
  3. Scheduler: ReduceLROnPlateau instead of cosine (adapts to loss plateau)
  4. Augmentation: properly applied during training batches
  5. Early stopping: patience increased to 8 to allow more learning time

Run:
  cd Backend/cooking_assistant
  python step2_train_sbert_fixed.py
"""

import json, os, random, time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report
from collections import Counter

# ── Reproducibility ────────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

# ── Config ─────────────────────────────────────────────────────────────────────
N_CLASSES     = 7
EMBED_DIM     = 384
HIDDEN_DIM    = 128
DROPOUT_P     = 0.3
LEARNING_RATE = 1e-3        # ← FIXED: was 2e-5 (50x too small for classifier head)
WEIGHT_DECAY  = 1e-4
BATCH_SIZE    = 16
MAX_EPOCHS    = 60          # more epochs since dataset is small
PATIENCE      = 8           # increased patience
GRAD_CLIP     = 1.0
N_FOLDS       = 5

CATEGORY_NAMES = {0:'Curry', 1:'Rice', 2:'Breakfast', 3:'Snack',
                  4:'Festival', 5:'Dessert', 6:'Beverage'}

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_FILE    = os.path.join(BASE_DIR, 'sbert_training_data.json')
CKPT_FILE    = os.path.join(BASE_DIR, 'sbert_model_checkpoint.pth')
RESULTS_FILE = os.path.join(BASE_DIR, 'sbert_training_results.json')


# ══════════════════════════════════════════════════════════════════════════════
# MODEL
# ══════════════════════════════════════════════════════════════════════════════

class RecipeClassifier(nn.Module):
    """
    Classifier head on top of frozen SBERT embeddings.
    Architecture: Linear(384→128) → ReLU → Dropout(0.3) → Linear(128→7)
    """
    def __init__(self, class_weights=None):
        super().__init__()
        self.fc1     = nn.Linear(EMBED_DIM, HIDDEN_DIM)
        self.relu    = nn.ReLU()
        self.dropout = nn.Dropout(DROPOUT_P)
        self.fc2     = nn.Linear(HIDDEN_DIM, N_CLASSES)

    def forward(self, x):
        return self.fc2(self.dropout(self.relu(self.fc1(x))))


# ══════════════════════════════════════════════════════════════════════════════
# DATASET
# ══════════════════════════════════════════════════════════════════════════════

class RecipeDataset(Dataset):
    def __init__(self, embeddings, labels):
        self.X = torch.FloatTensor(embeddings)
        self.y = torch.LongTensor(labels)
    def __len__(self): return len(self.y)
    def __getitem__(self, i): return self.X[i], self.y[i]


# ══════════════════════════════════════════════════════════════════════════════
# AUGMENTATION
# ══════════════════════════════════════════════════════════════════════════════

def augment_text(text, n=3):
    """Shuffle ingredient order to create n variants."""
    variants = [text]
    if 'Ingredients:' in text:
        prefix, rest = text.split('Ingredients:', 1)
        parts = [p.strip() for p in rest.split(',') if p.strip()]
        if len(parts) > 2:
            for _ in range(n):
                shuffled = parts.copy()
                random.shuffle(shuffled)
                variants.append(prefix + 'Ingredients: ' + ', '.join(shuffled))
    return variants


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING
# ══════════════════════════════════════════════════════════════════════════════

def compute_class_weights(labels):
    """
    Inverse frequency weighting — rare classes get higher weight.
    This stops the model from always predicting Curry.
    """
    counts = Counter(labels)
    total  = len(labels)
    weights = []
    for i in range(N_CLASSES):
        count = counts.get(i, 1)
        # Weight = total / (n_classes * class_count) — standard formula
        weights.append(total / (N_CLASSES * count))
    return torch.FloatTensor(weights)


def train_one_fold(X_train, y_train, X_val, y_val, fold_num, class_weights):
    train_ds = RecipeDataset(X_train, y_train)
    val_ds   = RecipeDataset(X_val,   y_val)
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_dl   = DataLoader(val_ds,   batch_size=BATCH_SIZE)

    model     = RecipeClassifier()
    optimizer = torch.optim.Adam(model.parameters(),
                                  lr=LEARNING_RATE,
                                  weight_decay=WEIGHT_DECAY)
    
    # Weighted cross-entropy — penalises wrong predictions on rare classes more
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    # ReduceLROnPlateau: halves LR when val_loss stops improving
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=4
    )

    best_val_loss  = float('inf')
    best_val_acc   = 0.0
    best_state     = None
    patience_count = 0
    best_epoch     = 0
    history        = []

    print(f"\n  ── Fold {fold_num}/5 ── (train={len(X_train)}, val={len(X_val)})")

    for epoch in range(MAX_EPOCHS):
        # ── Train ──
        model.train()
        t_preds, t_true = [], []
        for xb, yb in train_dl:
            optimizer.zero_grad()
            out  = model(xb)
            loss = criterion(out, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()
            t_preds.extend(out.argmax(1).tolist())
            t_true.extend(yb.tolist())
        train_acc = accuracy_score(t_true, t_preds)

        # ── Validate ──
        model.eval()
        v_preds, v_true, v_losses = [], [], []
        with torch.no_grad():
            for xb, yb in val_dl:
                out  = model(xb)
                loss = criterion(out, yb)
                v_losses.append(loss.item())
                v_preds.extend(out.argmax(1).tolist())
                v_true.extend(yb.tolist())
        val_loss = np.mean(v_losses)
        val_acc  = accuracy_score(v_true, v_preds)
        scheduler.step(val_loss)

        history.append({
            'epoch': epoch+1,
            'train_acc': round(train_acc, 4),
            'val_acc':   round(val_acc, 4),
            'val_loss':  round(val_loss, 4),
            'lr':        round(optimizer.param_groups[0]['lr'], 6),
        })

        # Print every 5 epochs
        if (epoch+1) % 5 == 0 or epoch < 5:
            print(f"  Ep {epoch+1:2d}/{MAX_EPOCHS} | "
                  f"train={train_acc:.3f} | "
                  f"val_loss={val_loss:.4f} | "
                  f"val_acc={val_acc:.3f} | "
                  f"lr={optimizer.param_groups[0]['lr']:.6f}")

        # Early stopping
        if val_loss < best_val_loss - 1e-5:
            best_val_loss  = val_loss
            best_val_acc   = val_acc
            best_state     = {k: v.clone() for k, v in model.state_dict().items()}
            patience_count = 0
            best_epoch     = epoch + 1
        else:
            patience_count += 1
            if patience_count >= PATIENCE:
                print(f"  [Early stop] epoch {epoch+1} | best was epoch {best_epoch}")
                break

    print(f"  Fold {fold_num} ✓  best_acc={best_val_acc:.4f} at epoch {best_epoch}")
    return best_val_acc, best_state, history


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("STEP 2 (FIXED) — SENTENCE-BERT CLASSIFIER TRAINING")
    print("=" * 65)

    # ── Load data ──
    if not os.path.exists(DATA_FILE):
        print(f"[✗] {DATA_FILE} not found. Run step1_prepare_data.py first!")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts  = [d['text']  for d in data]
    labels = [d['label'] for d in data]
    names  = [d['name']  for d in data]
    labels_arr = np.array(labels)

    print(f"\n[✓] {len(texts)} recipes loaded")
    dist = Counter(labels)
    print("[Category distribution]")
    for k, v in sorted(dist.items()):
        print(f"  {CATEGORY_NAMES[k]:12s}: {v:3d} recipes")

    # ── Compute class weights ──
    class_weights = compute_class_weights(labels)
    print(f"\n[Class weights] (higher = rarer category gets more attention)")
    for i, w in enumerate(class_weights):
        print(f"  {CATEGORY_NAMES[i]:12s}: {w:.3f}")

    # ── Load SBERT ──
    print(f"\n[Loading] all-MiniLM-L6-v2 ...")
    t0 = time.time()
    sbert = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"[✓] Loaded in {time.time()-t0:.1f}s")

    # ── Encode all recipes ──
    print(f"\n[Encoding] {len(texts)} recipes → 384-dim vectors ...")
    t0 = time.time()
    embeddings = sbert.encode(texts, show_progress_bar=True,
                               batch_size=32, convert_to_numpy=True)
    print(f"[✓] Done in {time.time()-t0:.1f}s | shape: {embeddings.shape}")

    # ── 5-Fold Cross Validation ──
    print(f"\n[Training] 5-Fold Stratified Cross-Validation")
    print(f"  LR={LEARNING_RATE}  dropout={DROPOUT_P}  "
          f"batch={BATCH_SIZE}  max_epochs={MAX_EPOCHS}  patience={PATIENCE}")
    print(f"  [Key fix] Using weighted CrossEntropyLoss to handle class imbalance")

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    fold_accs, fold_f1s, all_histories = [], [], []
    best_acc, best_state = 0.0, None
    best_preds, best_true = None, None

    for fold_idx, (train_idx, val_idx) in enumerate(
            skf.split(embeddings, labels_arr)):

        fold_num = fold_idx + 1

        X_train_base = embeddings[train_idx]
        y_train_base = labels_arr[train_idx]
        X_val        = embeddings[val_idx]
        y_val        = labels_arr[val_idx]

        # Augmentation: encode shuffled ingredient variants for training set only
        print(f"\n  [Augmenting fold {fold_num} training data] ...")
        aug_texts_fold  = []
        aug_labels_fold = []
        for i, idx in enumerate(train_idx):
            variants = augment_text(texts[idx], n=2)  # original + 2 shuffled
            aug_texts_fold.extend(variants)
            aug_labels_fold.extend([labels[idx]] * len(variants))

        # Only encode the extra augmented (skip index 0 = original already encoded)
        extra_texts  = []
        extra_labels = []
        ptr = 0
        for idx in train_idx:
            variants = augment_text(texts[idx], n=2)
            if len(variants) > 1:
                extra_texts.extend(variants[1:])       # skip original
                extra_labels.extend([labels[idx]] * (len(variants)-1))
            ptr += len(variants)

        if extra_texts:
            extra_embs = sbert.encode(extra_texts, show_progress_bar=False,
                                       batch_size=32, convert_to_numpy=True)
            X_train = np.vstack([X_train_base, extra_embs])
            y_train = np.concatenate([y_train_base, np.array(extra_labels)])
        else:
            X_train = X_train_base
            y_train = y_train_base

        print(f"  Train after augmentation: {len(X_train)} samples")

        val_acc, state, history = train_one_fold(
            X_train, y_train, X_val, y_val, fold_num, class_weights
        )
        fold_accs.append(val_acc)
        all_histories.append(history)

        # Get per-fold predictions
        model = RecipeClassifier()
        model.load_state_dict(state)
        model.eval()
        preds, true = [], []
        with torch.no_grad():
            for xb, yb in DataLoader(RecipeDataset(X_val, y_val),
                                      batch_size=BATCH_SIZE):
                preds.extend(model(xb).argmax(1).tolist())
                true.extend(yb.tolist())

        f1 = f1_score(true, preds, average='macro', zero_division=0)
        fold_f1s.append(f1)
        print(f"  Fold {fold_num} macro-F1 = {f1:.4f}")

        if val_acc > best_acc:
            best_acc, best_state = val_acc, state
            best_preds, best_true = preds, true

    # ── Final Results ──
    mean_acc = float(np.mean(fold_accs))
    std_acc  = float(np.std(fold_accs))
    mean_f1  = float(np.mean(fold_f1s))

    print("\n" + "=" * 65)
    print("RESULTS")
    print("=" * 65)
    print(f"Mean Accuracy  : {mean_acc:.4f}  ({mean_acc*100:.2f}%)")
    print(f"Std Deviation  : ±{std_acc:.4f}  (±{std_acc*100:.2f}%)")
    print(f"Mean Macro-F1  : {mean_f1:.4f}")
    print(f"Best Fold Acc  : {best_acc:.4f}  ({best_acc*100:.2f}%)")
    print(f"All Fold Accs  : {[f'{a:.4f}' for a in fold_accs]}")

    # Classify results quality
    if mean_acc >= 0.75:
        quality = "✅ EXCELLENT — ready to integrate"
    elif mean_acc >= 0.65:
        quality = "✅ GOOD — acceptable for paper"
    elif mean_acc >= 0.50:
        quality = "⚠️  FAIR — mention limitations in paper"
    else:
        quality = "❌ POOR — model needs more data or features"
    print(f"\nQuality: {quality}")

    if best_preds and best_true:
        print(f"\nPer-Class Report (best fold):")
        present = sorted(set(best_true))
        print(classification_report(
            best_true, best_preds,
            labels=present,
            target_names=[CATEGORY_NAMES[i] for i in present],
            zero_division=0
        ))

    # ── Save ──
    torch.save(best_state, CKPT_FILE)
    print(f"[✓] Model saved: {CKPT_FILE}")

    results = {
        'mean_accuracy':   round(mean_acc, 4),
        'std_accuracy':    round(std_acc,  4),
        'mean_macro_f1':   round(mean_f1,  4),
        'best_fold_acc':   round(best_acc, 4),
        'fold_accuracies': [round(a, 4) for a in fold_accs],
        'fold_f1s':        [round(f, 4) for f in fold_f1s],
        'n_recipes':       len(texts),
        'quality':         quality,
        'config': {
            'model':         'all-MiniLM-L6-v2',
            'learning_rate': LEARNING_RATE,
            'dropout':       DROPOUT_P,
            'batch_size':    BATCH_SIZE,
            'max_epochs':    MAX_EPOCHS,
            'patience':      PATIENCE,
            'class_weighted_loss': True,
            'seed':          SEED,
        },
        'fold_histories': all_histories,
    }
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Results saved: {RESULTS_FILE}")
    print(f"\n→ Next: python sbert_matcher.py  (to test it works)")
    print(f"→ Then: update routes.py using step4_routes_update.py")

    return mean_acc


if __name__ == '__main__':
    main()