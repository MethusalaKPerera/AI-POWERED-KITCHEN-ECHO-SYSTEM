#!/usr/bin/env python3
"""
=============================================================================
Generate Cross-Cultural Robustness Figures — GAP 4 for Conference Submission
=============================================================================
IT22131942 · Spontaneous Cooking Assistant Research
Input:  figures/cross_cultural_results.json  (from cross_cultural_evaluation.py)
Outputs:
  figures/cross_cultural_similarity.png  — Box plot (cosine sim by culture)
  figures/recipe_embedding_tsne.png      — t-SNE scatter (color-coded by culture)
=============================================================================
Run: python generate_cross_cultural_figure.py
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

BASE_DIR    = Path(__file__).parent
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)
INPUT_JSON  = FIGURES_DIR / "cross_cultural_results.json"

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   10,
    "figure.dpi":        300,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# Culture → color mapping (colorblind-friendly)
CULTURE_COLORS = {
    "Sri Lankan":      "#D55E00",   # vermillion
    "South Indian":    "#0072B2",   # blue
    "Southeast Asian": "#009E73",   # green
    "General Asian":   "#E69F00",   # amber
}
CULTURE_MARKERS = {
    "Sri Lankan":      "o",
    "South Indian":    "s",
    "Southeast Asian": "^",
    "General Asian":   "D",
}


def load_data():
    if not INPUT_JSON.exists():
        print(f"ERROR: {INPUT_JSON} not found — run cross_cultural_evaluation.py first.")
        raise SystemExit(1)
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — BOX PLOT OF COSINE SIMILARITY DISTRIBUTIONS
# ═══════════════════════════════════════════════════════════════════════════

def plot_similarity_boxplot(data: dict):
    sim_data = data["cosine_similarity_distributions"]

    labels = ["Sri Lankan\n(Within)", "South Indian\n(vs SL)",
               "SE Asian\n(vs SL)", "General Asian\n(vs SL)"]
    keys   = ["SL_within", "South Indian", "Southeast Asian", "General Asian"]
    colors = [CULTURE_COLORS["Sri Lankan"], CULTURE_COLORS["South Indian"],
              CULTURE_COLORS["Southeast Asian"], CULTURE_COLORS["General Asian"]]

    box_data = []
    for k in keys:
        vals = sim_data.get(k, {}).get("values", [0.5])
        box_data.append(vals)

    fig, ax = plt.subplots(figsize=(9, 5.5))

    bp = ax.boxplot(
        box_data,
        patch_artist=True,
        widths=0.5,
        medianprops=dict(color="black", linewidth=2.0),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        flierprops=dict(marker="o", markersize=3.5, alpha=0.5),
        notch=False,
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.72)

    # Overlay individual points (jittered strip)
    rng = np.random.default_rng(42)
    for i, vals in enumerate(box_data, start=1):
        jitter = rng.uniform(-0.18, 0.18, size=min(len(vals), 150))
        sample = np.array(vals[:150])
        ax.scatter(
            np.full(len(sample), i) + jitter, sample,
            color=colors[i - 1], alpha=0.35, s=10, zorder=3
        )

    # Means
    for i, vals in enumerate(box_data, start=1):
        ax.scatter([i], [np.mean(vals)], color="white", edgecolors="black",
                   s=55, zorder=5, marker="D", linewidths=1.2)

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Cosine Similarity with Sri Lankan Recipes")
    ax.set_ylim(0.0, 1.05)
    ax.set_title(
        "Recipe Embedding Similarity: Sri Lankan vs. Cross-Cultural Cuisines\n"
        "(Sentence-BERT all-MiniLM-L6-v2 · IT22131942)",
        fontweight="bold"
    )
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.35, linewidth=0.7)

    # Annotation: cultural proximity interpretation
    means = [np.mean(d) for d in box_data]
    for i, (lbl, mean) in enumerate(zip(["SL", "SI", "SEA", "GA"], means), start=1):
        ax.text(i, mean + 0.03, f"μ={mean:.3f}",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold",
                color=colors[i - 1])

    # Legend for diamond = mean
    diamond_patch = mpatches.Patch(facecolor="white", edgecolor="black",
                                   label="◆ = Mean")
    ax.legend(handles=[diamond_patch], loc="lower right", framealpha=0.9)

    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "cross_cultural_similarity.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅ cross_cultural_similarity.png saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2 — t-SNE EMBEDDING VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════

def plot_tsne(data: dict):
    tsne_data = data["tsne_visualization"]
    coords    = np.array(tsne_data["coords"])
    cultures  = tsne_data["cultures"]
    names     = tsne_data["names"]

    unique_cultures = list(CULTURE_COLORS.keys())

    fig, ax = plt.subplots(figsize=(10, 7))

    handles = []
    for culture in unique_cultures:
        mask   = [i for i, c in enumerate(cultures) if c == culture]
        if not mask:
            continue
        pts    = coords[mask]
        color  = CULTURE_COLORS[culture]
        marker = CULTURE_MARKERS[culture]
        size   = 90 if culture == "Sri Lankan" else 70
        alpha  = 0.85

        sc = ax.scatter(
            pts[:, 0], pts[:, 1],
            c=color, marker=marker, s=size, alpha=alpha,
            edgecolors="white", linewidths=0.6, zorder=4,
            label=culture
        )
        # Label a few points
        label_every = max(1, len(mask) // 5)
        for j, idx in enumerate(mask[::label_every][:3]):
            short_name = names[idx][:18] + ("…" if len(names[idx]) > 18 else "")
            ax.annotate(
                short_name,
                xy=coords[idx],
                xytext=(coords[idx, 0] + 1.5, coords[idx, 1] + 1.0),
                fontsize=6.5,
                color=color,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.5),
                alpha=0.85
            )
        handles.append(mpatches.Patch(facecolor=color, edgecolor="grey",
                                      linewidth=0.8, label=culture))

    ax.set_xlabel("t-SNE Component 1", labelpad=6)
    ax.set_ylabel("t-SNE Component 2", labelpad=6)
    ax.set_title(
        "t-SNE Visualisation of Recipe Embeddings by Culture\n"
        "(Sentence-BERT · Sri Lankan + Cross-Cultural Recipes · IT22131942)",
        fontweight="bold"
    )
    legend = ax.legend(
        handles=handles, loc="best",
        framealpha=0.90, edgecolor="#aaaaaa",
        ncol=2
    )

    # Remove axis ticks (t-SNE values are unitless)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)

    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "recipe_embedding_tsne.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅ recipe_embedding_tsne.png saved → {out}")


def main():
    print("\n" + "=" * 60)
    print("  GENERATE CROSS-CULTURAL FIGURES — GAP 4")
    print("=" * 60)
    data = load_data()
    print("\n[Figure 1/2] Cosine similarity box plot...")
    plot_similarity_boxplot(data)
    print("[Figure 2/2] t-SNE recipe embedding visualisation...")
    plot_tsne(data)
    print("\n   Done! Open figures/ to view cross-cultural figures.\n")


if __name__ == "__main__":
    main()
