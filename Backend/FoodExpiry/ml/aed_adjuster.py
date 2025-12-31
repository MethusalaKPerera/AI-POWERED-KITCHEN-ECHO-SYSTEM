# FoodExpiry/ml/aed_adjuster.py

from typing import Dict, Tuple, Any


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(x, hi))


def _init_stats() -> Dict[str, Any]:
    return {"n": 0, "early": 0, "on_time": 0, "late": 0, "confidence": 0.0}


def _update_stats(stats: Dict[str, Any], feedback: str) -> Dict[str, Any]:
    stats = dict(stats or _init_stats())
    stats["n"] = int(stats.get("n", 0)) + 1

    if feedback == "early":
        stats["early"] = int(stats.get("early", 0)) + 1
    elif feedback == "late":
        stats["late"] = int(stats.get("late", 0)) + 1
    else:
        stats["on_time"] = int(stats.get("on_time", 0)) + 1

    # confidence increases with sample size, capped
    stats["confidence"] = _clamp(stats["n"] / 20.0, 0.0, 0.85)
    return stats


# ---------------------------------------------------------
# APPLY AED (Issue B + C)
# Item-level -> Category-level -> No-history fallback
# Uses biological bounds: 0.5× to 1.5× base expiry
# ---------------------------------------------------------
def apply_aed(
    user_adjustments: Dict,
    item_name: str,
    category: str,
    predicted_days: float,
    base_days: float
) -> float:
    """
    Apply AED with hierarchy:
      1) item:<item_name>
      2) category:<category>
      3) fallback: 0

    Safety bounds:
      0.5×base_days <= final_days <= 1.5×base_days
    """
    user_adjustments = user_adjustments or {}

    item_key = f"item:{(item_name or '').lower().strip()}"
    cat_key = f"category:{(category or '').lower().strip()}"

    delta = 0.0
    if item_key in user_adjustments:
        delta = float(user_adjustments.get(item_key) or 0.0)
    elif cat_key in user_adjustments:
        delta = float(user_adjustments.get(cat_key) or 0.0)

    adjusted = float(predicted_days) + delta

    # Issue B: biological bounds (your novelty says 0.5× to 1.5×)
    min_days = 0.5 * float(base_days)
    max_days = 1.5 * float(base_days)

    return _clamp(adjusted, min_days, max_days)


# ---------------------------------------------------------
# UPDATE AED FROM FEEDBACK
# We update BOTH:
#   - item-level (faster adaptation)
#   - category-level (slower, stable)
# ---------------------------------------------------------
def update_aed_single(
    previous_adj: float,
    feedback: str,
    actual_days: float,
    predicted_days: float,
    stats: Dict[str, Any],
    learning_rate: float
) -> Tuple[float, Dict[str, Any]]:
    """
    Update ONE AED value (either item-level or category-level).
    - learning_rate controls how fast it changes.
      recommended: item 0.7, category 0.3
    """
    previous_adj = float(previous_adj or 0.0)
    stats = _update_stats(stats, feedback)

    # error = actual - predicted (positive means it lasted longer than predicted)
    error = float(actual_days) - float(predicted_days)

    # scale down updates as confidence increases
    effective_lr = float(learning_rate) * (1.0 - float(stats["confidence"]))
    delta = error * effective_lr

    # avoid runaway
    delta = _clamp(delta, -3.0, 3.0)

    # apply decay to keep it stable over time
    new_adj = previous_adj * 0.95 + delta

    # clamp adjustment
    new_adj = _clamp(new_adj, -7.0, 7.0)

    return new_adj, stats
