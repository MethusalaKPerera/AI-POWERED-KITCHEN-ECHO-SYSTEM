# FoodExpiry/ml/aed_adjuster.py

def apply_aed(user_adjustments, category, ml_days, base_days=None):
    """
    Advanced AED – Applies adaptive expiry drift correction.
    
    Inputs:
        user_adjustments: dict from MongoDB
        category: str
        ml_days: ML predicted final days (already corrected)
        base_days: optional base expiry for stability
    
    Returns:
        corrected_days: final result after AED
    """

    # ----------------------------------------------
    # 1. Base adjustment for this category
    # ----------------------------------------------
    old_adj = user_adjustments.get(category, 0)

    # ----------------------------------------------
    # 2. Optional stability: prevent unrealistic results
    # ----------------------------------------------
    if base_days is not None:
        min_limit = base_days * 0.40
        max_limit = base_days * 1.50
    else:
        min_limit = 1
        max_limit = 60

    # ----------------------------------------------
    # 3. Apply adjustment
    # ----------------------------------------------
    corrected = ml_days + old_adj

    # clamp
    if corrected < min_limit:
        corrected = min_limit
    if corrected > max_limit:
        corrected = max_limit

    return int(round(corrected))



def update_aed(previous_adj, category_feedback, actual_days, predicted_days, stats):
    """
    Compute the NEW adjustment for this category.

    Inputs:
        previous_adj: existing AED value for category
        category_feedback: early / late / on_time
        actual_days: actual spoilage
        predicted_days: ml + previous AED
        stats: feedback stats for the category (dict)

    Outputs:
        new_adj, updated_stats
    """

    # ----------------------------------------------
    # 1. Determine delta weight
    # ----------------------------------------------
    if category_feedback == "early":
        delta = -1.5
    elif category_feedback == "late":
        delta = +1.5
    else:
        delta = +0.5  # on_time strengthens stability

    # ----------------------------------------------
    # 2. Reliability Filter (prevents bad feedback)
    # ----------------------------------------------
    if category_feedback == "early" and actual_days > predicted_days:
        delta = 0

    if category_feedback == "late" and actual_days < predicted_days:
        delta = 0

    # ----------------------------------------------
    # 3. Update stats
    # ----------------------------------------------
    stats = stats or {"total": 0, "early": 0, "late": 0, "on_time": 0, "confidence": 0}

    stats["total"] += 1
    if category_feedback == "early": stats["early"] += 1
    elif category_feedback == "late": stats["late"] += 1
    else: stats["on_time"] += 1

    # confidence = (on_time% - error%)
    stats["confidence"] = (
        (stats["on_time"] / stats["total"]) -
        ((stats["early"] + stats["late"]) / stats["total"])
    )

    # ----------------------------------------------
    # 4. Scale delta by confidence
    # ----------------------------------------------
    effective_delta = delta * (1 - stats["confidence"])
    effective_delta = max(-2, min(2, effective_delta))

    # ----------------------------------------------
    # 5. Exponential decay + delta
    # ----------------------------------------------
    new_adj = previous_adj * 0.95 + effective_delta

    # clamp
    new_adj = max(-5, min(5, new_adj))

    return new_adj, stats
