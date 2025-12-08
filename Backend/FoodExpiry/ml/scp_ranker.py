def scp_score(days_left):
    if days_left <= 2:
        return 1.0
    elif days_left <= 5:
        return 0.7
    else:
        return 0.4
