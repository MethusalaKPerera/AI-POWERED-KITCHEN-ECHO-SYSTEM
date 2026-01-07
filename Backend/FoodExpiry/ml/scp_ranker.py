def scp_score(days_left: float) -> float:
    """
    Smart Consumption Priority (SCP)
    Input MUST be: days remaining from TODAY until expiry (not total shelf life).
    """
    try:
        d = float(days_left)
    except Exception:
        d = 9999.0

    if d <= 2:
        return 1.0
    elif d <= 5:
        return 0.7
    else:
        return 0.4
