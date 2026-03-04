#!/usr/bin/env python3
"""
=============================================================================
Generate Baseline Comparison Figure — GAP 1 for Conference Submission
=============================================================================
IT22131942 · Spontaneous Cooking Assistant Research
Input:  figures/baseline_results.json  (from baseline_comparison.py)
Output: figures/baseline_comparison.png  (300 DPI, publication-ready)

Chart: Grouped bar chart — Accuracy / Precision / Recall / F1-macro
       for TF-IDF+SVM, TF-IDF+LR, BoW+NB, and Sentence-BERT
=============================================================================
Run: python generate_baseline_figure.py
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)
INPUT_JSON  = FIGURES_DIR / "baseline_results.json"
OUTPUT_PNG  = FIGURES_DIR / "baseline_comparison.png"


# ── Publication-ready style ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   13,
    "axes.labelsize":   11,
    "xtick.labelsize":  10,
    "ytick.labelsize":  10,
    "legend.fontsize":  10,
    "figure.dpi":       300,
    "axes.spines.top":  False,
    "axes.spines.right":False,
})

# Colorblind-friendly palette (Wong 2011)
PALETTE = {
    "Accuracy":  "#0072B2",   # blue
    "Precision": "#E69F00",   # amber
    "Recall":    "#009E73",   # green
    "F1-macro":  "#CC79A7",   # pink/mauve
}

MODEL_COLORS = [
    "#999999",   # TF-IDF + SVM        — grey
    "#56B4E9",   # TF-IDF + LR         — light blue
    "#F0E442",   # BoW + Naive Bayes   — yellow
    "#D55E00",   # Sentence-BERT       — vermillion (stands out)
]


def load_results():
    if not INPUT_JSON.exists():
        print(f"ERROR: {INPUT_JSON} not found — run baseline_comparison.py first.")
        raise SystemExit(1)
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def make_figure(data: dict):
    models = data["models"]
    names  = [m["name"].replace("Sentence-BERT (Proposed)", "Sentence-BERT★")
              for m in models]

    metrics = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    metric_labels = ["Accuracy", "Precision\n(Macro)", "Recall\n(Macro)", "F1-Score\n(Macro)"]
    std_keys = ["accuracy_std", "precision_macro_std", "recall_macro_std", "f1_macro_std"]

    n_models  = len(models)
    n_metrics = len(metrics)
    bar_width = 0.18
    bar_gap   = 0.04

    # Positions
    group_centers = np.arange(n_metrics)
    offsets = np.linspace(
        -(n_models - 1) / 2 * (bar_width + bar_gap),
         (n_models - 1) / 2 * (bar_width + bar_gap),
        n_models
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    bars_for_legend = []
    for i, model in enumerate(models):
        vals  = [model.get(k, 0.0) for k in metrics]
        stds  = [model.get(s, 0.0) for s in std_keys]
        pos   = group_centers + offsets[i]
        color = MODEL_COLORS[i % len(MODEL_COLORS)]
        is_sbert = "Sentence-BERT" in model["name"]

        bars = ax.bar(
            pos, vals, bar_width,
            color=color,
            edgecolor="black" if is_sbert else "none",
            linewidth=1.4 if is_sbert else 0,
            alpha=0.92,
            yerr=stds,
            capsize=3,
            error_kw=dict(elinewidth=1.0, ecolor="#333333"),
            zorder=3,
        )
        bars_for_legend.append(bars[0])

        # Annotate Sentence-BERT bars with value labels
        if is_sbert:
            for bar, val in zip(bars, vals):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.012,
                    f"{val*100:.1f}%",
                    ha="center", va="bottom", fontsize=8.5,
                    fontweight="bold", color="#D55E00"
                )

    # ── Axes formatting ──────────────────────────────────────────────────
    ax.set_xticks(group_centers)
    ax.set_xticklabels(metric_labels)
    ax.set_ylim(0, 1.10)
    ax.set_yticks(np.arange(0, 1.05, 0.1))
    ax.set_yticklabels([f"{v*100:.0f}%" for v in np.arange(0, 1.05, 0.1)])
    ax.set_ylabel("Score (%)")
    ax.set_title(
        "Classification Performance: Baseline vs. Proposed Approach\n"
        "(5-Fold Stratified Cross-Validation · IT22131942)",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.axhline(y=0.8684, color="#D55E00", linestyle="--", linewidth=1.2,
               alpha=0.45, zorder=1)
    ax.text(n_metrics - 0.05, 0.8684 + 0.008, "BERT 86.8%",
            color="#D55E00", fontsize=8.5, ha="right")
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, linewidth=0.8)

    # ── Legend ───────────────────────────────────────────────────────────
    legend_names = [n.replace("★", " ★ (Proposed)") for n in names]
    legend = ax.legend(
        bars_for_legend, legend_names,
        loc="upper left", framealpha=0.9, edgecolor="#cccccc",
        fontsize=9.5, ncol=2
    )

    # ── Superiority annotation ────────────────────────────────────────────
    best_baseline_acc = max(
        m.get("accuracy", 0) for m in models if "Sentence-BERT" not in m["name"]
    )
    sbert_acc = next(
        m.get("accuracy", 0) for m in models if "Sentence-BERT" in m["name"]
    )
    improvement = (sbert_acc - best_baseline_acc) / best_baseline_acc * 100

    ax.annotate(
        f"Sentence-BERT outperforms\nbest baseline by +{improvement:.1f}%",
        xy=(0 + offsets[-1], sbert_acc),
        xytext=(0.5, 0.93),
        textcoords="axes fraction",
        fontsize=9.5,
        color="#D55E00",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#D55E00", lw=1.4),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#D55E00", alpha=0.85)
    )

    plt.tight_layout(pad=1.5)
    fig.savefig(OUTPUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✅ Figure saved → {OUTPUT_PNG}")


def main():
    print("\n" + "=" * 60)
    print("  GENERATE BASELINE COMPARISON FIGURE — GAP 1")
    print("=" * 60)
    data = load_results()
    make_figure(data)
    print("   Done! Open figures/baseline_comparison.png\n")


if __name__ == "__main__":
    main()
