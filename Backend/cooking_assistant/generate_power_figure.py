#!/usr/bin/env python3
"""
=============================================================================
Generate Power Analysis Figures — GAP 3 for Conference Submission
=============================================================================
IT22131942 · Spontaneous Cooking Assistant Research
Input:  figures/power_analysis_results.json  (from expanded_validation.py)
Outputs:
  figures/power_analysis.png           — Power curves vs n
  figures/bootstrap_distribution.png  — Bootstrap CI distribution
=============================================================================
Run: python generate_power_figure.py
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

BASE_DIR    = Path(__file__).parent
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)
INPUT_JSON  = FIGURES_DIR / "power_analysis_results.json"

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


def load_data():
    if not INPUT_JSON.exists():
        print(f"ERROR: {INPUT_JSON} not found — run expanded_validation.py first.")
        raise SystemExit(1)
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _compute_power(n_values, d, alpha=0.05):
    """Vectorised power calculation for a range of n values."""
    powers = []
    for n in n_values:
        df  = n - 1
        ncp = d * np.sqrt(n)
        t_crit = stats.t.ppf(1 - alpha, df)
        power  = 1 - stats.nct.cdf(t_crit, df, ncp)
        powers.append(float(np.clip(power, 0, 1)))
    return np.array(powers)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — POWER CURVES
# ═══════════════════════════════════════════════════════════════════════════

def plot_power_curves(data: dict):
    n_vals = np.arange(5, 201, 1)

    effect_configs = [
        (0.5,  "#56B4E9", "-",  "d = 0.5 (small)"),
        (0.8,  "#009E73", "--", "d = 0.8 (medium)"),
        (1.0,  "#E69F00", "-.", "d = 1.0 (large)"),
        (3.18, "#D55E00", ":",  "d = 3.18 (observed, this study)"),
    ]

    n_current = data["metadata"]["participants"]
    observed_d = data["power_analysis"]["observed_cohen_d"]

    fig, ax = plt.subplots(figsize=(9, 5.5))

    for d, color, ls, label in effect_configs:
        pows = _compute_power(n_vals, d)
        ax.plot(n_vals, pows, color=color, linestyle=ls,
                linewidth=2.0, label=label, zorder=3)

    # 80% power reference line
    ax.axhline(0.80, color="#666666", linewidth=1.0, linestyle="--",
               alpha=0.6, label="80% power threshold", zorder=2)

    # Mark current study n=15
    ax.axvline(n_current, color="#333333", linewidth=1.2, linestyle=":",
               alpha=0.7, zorder=2)
    power_at_n15 = _compute_power([n_current], observed_d)[0]
    ax.scatter([n_current], [power_at_n15], s=80, color="#D55E00",
               zorder=5, marker="★")
    ax.text(n_current + 3, power_at_n15 - 0.07,
            f"Current study\nn=15, power={power_at_n15*100:.0f}%",
            fontsize=9, color="#D55E00",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#D55E00", alpha=0.85))

    # Mark planned Phase 2 n=50
    ax.axvline(50, color="#009E73", linewidth=1.0, linestyle=":",
               alpha=0.50, zorder=2)
    ax.text(52, 0.12, "Phase 2\n(n=50)", fontsize=8.5, color="#009E73")

    ax.set_xlim(5, 200)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Sample Size (n)", labelpad=6)
    ax.set_ylabel("Statistical Power (1 − β)", labelpad=6)
    ax.set_title(
        "Statistical Power vs. Sample Size\n"
        "(One-Sample t-Test, α = 0.05 · IT22131942)",
        fontweight="bold"
    )
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.set_yticklabels([f"{v:.0%}" for v in np.arange(0, 1.1, 0.1)])
    ax.legend(loc="lower right", framealpha=0.9, edgecolor="#cccccc")
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.3, linewidth=0.7)

    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "power_analysis.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅ power_analysis.png saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2 — BOOTSTRAP DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════

def plot_bootstrap_distribution(data: dict):
    bootstrap = data["bootstrap"]
    # Regenerate full distribution from raw data
    raw_reductions = data["metadata"]["reduction_pct"]

    rng = np.random.default_rng(2024)
    arr = np.array(raw_reductions)
    boot_means = np.array([
        float(np.mean(rng.choice(arr, size=len(arr), replace=True)))
        for _ in range(10_000)
    ])

    ci_l = bootstrap["ci_95_lower"]
    ci_u = bootstrap["ci_95_upper"]
    mean_val = bootstrap["observed_mean_reduction"]

    fig, ax = plt.subplots(figsize=(8, 4.5))

    # Histogram
    n_hist, bins, patches = ax.hist(
        boot_means, bins=50, density=True,
        color="#56B4E9", edgecolor="white", alpha=0.80, linewidth=0.6
    )
    # Shade CI region
    ci_mask = (bins[:-1] >= ci_l) & (bins[:-1] <= ci_u)
    for patch, in_ci in zip(patches, ci_mask):
        if in_ci:
            patch.set_facecolor("#0072B2")
            patch.set_alpha(0.90)

    # KDE overlay
    bw = 1.06 * boot_means.std() * len(boot_means) ** (-0.2)
    x = np.linspace(boot_means.min() - 3, boot_means.max() + 3, 300)
    kde = np.array([np.mean(stats.norm.pdf(x_i, boot_means, bw)) for x_i in x])
    ax.plot(x, kde, color="#0072B2", linewidth=2.2, label="Bootstrap KDE")

    # Reference lines
    ax.axvline(mean_val, color="#D55E00", linewidth=2.0, linestyle="-",
               label=f"Observed mean = {mean_val:.1f}%")
    ax.axvline(ci_l, color="#333333", linewidth=1.5, linestyle="--",
               label=f"95% CI [{ci_l:.1f}%, {ci_u:.1f}%]")
    ax.axvline(ci_u, color="#333333", linewidth=1.5, linestyle="--")

    # Shading annotation
    ax.fill_betweenx(
        [0, max(n_hist) * 0.15], ci_l, ci_u,
        color="#0072B2", alpha=0.12
    )
    ax.text((ci_l + ci_u) / 2, max(n_hist) * 0.08,
            "95% CI", ha="center", fontsize=9, color="#0072B2", fontweight="bold")

    ax.set_xlabel("Food Waste Reduction (%)", labelpad=6)
    ax.set_ylabel("Density", labelpad=6)
    ax.set_title(
        f"Bootstrap Distribution of Food Waste Reduction\n"
        f"(10,000 Resamples from n=15 · 95% CI: [{ci_l:.1f}%, {ci_u:.1f}%])",
        fontweight="bold"
    )
    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)

    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "bootstrap_distribution.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅ bootstrap_distribution.png saved → {out}")


def main():
    print("\n" + "=" * 60)
    print("  GENERATE POWER ANALYSIS FIGURES — GAP 3")
    print("=" * 60)
    data = load_data()
    print("\n[Figure 1/2] Power curves (4 effect sizes)...")
    plot_power_curves(data)
    print("[Figure 2/2] Bootstrap CI distribution...")
    plot_bootstrap_distribution(data)
    print("\n   Done! Open figures/ to view the power analysis figures.\n")


if __name__ == "__main__":
    main()
