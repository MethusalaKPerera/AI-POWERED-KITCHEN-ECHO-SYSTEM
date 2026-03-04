#!/usr/bin/env python3
"""
=============================================================================
Generate Confusion Matrix Figures — GAP 2 for Conference Submission
=============================================================================
IT22131942 · Spontaneous Cooking Assistant Research
Input:  figures/vision_evaluation_data.json  (from vision_evaluation.py)
Outputs:
  figures/confusion_matrix.png         — 15×15 heatmap (seaborn)
  figures/per_ingredient_metrics.png   — P/R/F1 bar chart (top 20)
  figures/confidence_distribution.png  — confidence score histogram
All: 300 DPI, colorblind-friendly, publication fonts.
=============================================================================
Run: python generate_confusion_matrix.py
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR    = Path(__file__).parent
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)
INPUT_JSON  = FIGURES_DIR / "vision_evaluation_data.json"

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "axes.titlesize":    12,
    "axes.labelsize":    10,
    "xtick.labelsize":   8.5,
    "ytick.labelsize":   8.5,
    "legend.fontsize":   9,
    "figure.dpi":        300,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})


def load_data():
    if not INPUT_JSON.exists():
        print(f"ERROR: {INPUT_JSON} not found — run vision_evaluation.py first.")
        raise SystemExit(1)
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — CONFUSION MATRIX HEATMAP (15×15)
# ═══════════════════════════════════════════════════════════════════════════

def plot_confusion_matrix(data: dict):
    cm_data = data["confusion_matrix"]
    categories = cm_data["categories"]
    cm = np.array(cm_data["matrix"], dtype=float)

    # Normalise rows to proportions
    row_sums = cm.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    cm_norm = cm / row_sums

    # Readable category names
    display_names = [c.replace("_", "\n") for c in categories]

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        cm_norm,
        ax=ax,
        annot=True,
        fmt=".2f",
        cmap="Blues",           # colorblind-friendly sequential
        xticklabels=display_names,
        yticklabels=display_names,
        linewidths=0.4,
        linecolor="#dddddd",
        cbar_kws={"label": "Detection Rate (row-normalised)", "shrink": 0.85},
        vmin=0.0, vmax=1.0,
        annot_kws={"size": 7.5},
    )
    ax.set_title(
        "Ingredient Detection Confusion Matrix\n"
        "(Simulated from 3-Week Study · n=15 · 847 Detection Events)",
        fontsize=12, fontweight="bold", pad=10
    )
    ax.set_xlabel("Detected Ingredient", labelpad=8)
    ax.set_ylabel("Ground Truth Ingredient", labelpad=8)

    # Highlight key confusion pairs
    for pair in [("curry_leaves", "pandan_leaf"), ("turmeric_powder", "curry_powder")]:
        try:
            row_i = categories.index(pair[0])
            col_j = categories.index(pair[1])
            ax.add_patch(plt.Rectangle((col_j, row_i), 1, 1,
                         fill=False, edgecolor="#D55E00", linewidth=2.5))
            ax.add_patch(plt.Rectangle((row_i, col_j), 1, 1,
                         fill=False, edgecolor="#D55E00", linewidth=2.5))
        except ValueError:
            pass

    # Legend for orange boxes
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor="none", edgecolor="#D55E00",
                             linewidth=2.5, label="Key confusion pair")]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "confusion_matrix.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅ confusion_matrix.png saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2 — PER-INGREDIENT PRECISION / RECALL BAR CHART (TOP 20)
# ═══════════════════════════════════════════════════════════════════════════

def plot_per_ingredient_metrics(data: dict):
    pim   = data["per_ingredient_metrics"]
    names = pim["ingredients"]
    metrics = pim["metrics"]

    precisions = [metrics[n]["precision"] for n in names]
    recalls    = [metrics[n]["recall"]    for n in names]
    f1s        = [metrics[n]["f1"]        for n in names]

    # Sort by F1 descending for readability
    order = sorted(range(len(names)), key=lambda i: f1s[i], reverse=True)
    names_sorted = [names[i].replace("_", "\n") for i in order]
    prec_sorted  = [precisions[i] for i in order]
    rec_sorted   = [recalls[i]    for i in order]
    f1_sorted    = [f1s[i]        for i in order]

    x = np.arange(len(names_sorted))
    width = 0.27

    fig, ax = plt.subplots(figsize=(14, 5.5))
    b1 = ax.bar(x - width, prec_sorted, width, label="Precision", color="#0072B2", alpha=0.88)
    b2 = ax.bar(x,         rec_sorted,  width, label="Recall",    color="#009E73", alpha=0.88)
    b3 = ax.bar(x + width, f1_sorted,   width, label="F1-Score",  color="#CC79A7", alpha=0.88)

    ax.set_xticks(x)
    ax.set_xticklabels(names_sorted, rotation=0, ha="center", fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.set_yticklabels([f"{v:.0%}" for v in np.arange(0, 1.1, 0.1)])
    ax.set_ylabel("Score")
    ax.set_title(
        "Per-Ingredient Precision / Recall / F1 — Vision Detection\n"
        "(Top 20 Ingredients · Sorted by F1-Score)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(loc="lower right", framealpha=0.9)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.35, linewidth=0.7)

    # Annotate worst-F1 ingredient
    worst_i = f1_sorted.index(min(f1_sorted))
    ax.annotate(
        "Hardest\nto detect",
        xy=(worst_i + width, f1_sorted[worst_i] + 0.01),
        xytext=(worst_i + width + 1.2, f1_sorted[worst_i] + 0.14),
        fontsize=8, color="#CC0000",
        arrowprops=dict(arrowstyle="->", color="#CC0000", lw=1.2)
    )

    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "per_ingredient_metrics.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅ per_ingredient_metrics.png saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3 — CONFIDENCE SCORE DISTRIBUTION HISTOGRAM
# ═══════════════════════════════════════════════════════════════════════════

def plot_confidence_distribution(data: dict):
    stats  = data["confidence_score_statistics"]
    scores = np.array(stats["all_scores"])
    mean   = stats["mean"]
    std    = stats["std"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    n, bins, patches = ax.hist(
        scores, bins=20, color="#56B4E9", edgecolor="white",
        alpha=0.85, density=True, linewidth=0.8
    )
    # Colour bars below 0.5 red (unreliable)
    for patch, left_edge in zip(patches, bins[:-1]):
        if left_edge < 0.5:
            patch.set_facecolor("#CC0000")
            patch.set_alpha(0.65)

    # Overlay KDE (manual normal curve)
    x = np.linspace(scores.min() - 0.05, scores.max() + 0.05, 200)
    gaussian = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
    ax.plot(x, gaussian, color="#0072B2", linewidth=2, label="KDE (Normal approx.)")
    ax.axvline(x=mean, color="#D55E00", linewidth=1.8, linestyle="--",
               label=f"Mean = {mean:.2f}")
    ax.axvline(x=0.5, color="#CC0000", linewidth=1.2, linestyle=":",
               label="Acceptance threshold (0.50)", alpha=0.8)

    ax.set_xlabel("Detection Confidence Score", labelpad=6)
    ax.set_ylabel("Density", labelpad=6)
    ax.set_title(
        "Vision API Detection Confidence Score Distribution\n"
        "(Red = below 0.50 acceptance threshold)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)

    # Annotation
    high_conf_pct = np.mean(scores >= 0.7) * 100
    ax.text(0.73, ax.get_ylim()[1] * 0.85,
            f"{high_conf_pct:.1f}% detections\n≥ 0.70 confidence",
            fontsize=9, color="#009E73",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#009E73", alpha=0.8))

    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "confidence_distribution.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅ confidence_distribution.png saved → {out}")


def main():
    print("\n" + "=" * 60)
    print("  GENERATE CONFUSION MATRIX FIGURES — GAP 2")
    print("=" * 60)
    data = load_data()
    print("\n[Figure 1/3] Confusion matrix heatmap (15×15)...")
    plot_confusion_matrix(data)
    print("[Figure 2/3] Per-ingredient P/R/F1 bar chart (top 20)...")
    plot_per_ingredient_metrics(data)
    print("[Figure 3/3] Confidence score distribution...")
    plot_confidence_distribution(data)
    print("\n   Done! Open figures/ to view the three figures.\n")


if __name__ == "__main__":
    main()
