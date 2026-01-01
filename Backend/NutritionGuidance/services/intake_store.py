# backend/NutritionGuidance/services/intake_store.py

import json
import os
from datetime import datetime, timedelta

from NutritionGuidance.services.dataset_loader import get_datasets


def _intake_path(app, user_id: str) -> str:
    store_dir = app.config.get("STORE_DIR") or os.path.join(os.getcwd(), "store")
    os.makedirs(store_dir, exist_ok=True)
    return os.path.join(store_dir, f"intake_{user_id}.json")


def add_intake(app, user_id: str, food_id: str, food_name: str, quantity: float, date_str: str) -> dict:
    """
    Store one intake record (a meal/log).
    quantity = number of servings (based on your dataset serving size)
    date_str = YYYY-MM-DD
    """
    user_id = (user_id or "demo").strip() or "demo"
    food_id = (food_id or "").strip()
    food_name = (food_name or "").strip()

    # Validate date
    try:
        _ = datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")

    try:
        quantity = float(quantity)
    except Exception:
        quantity = 1.0

    if quantity <= 0:
        raise ValueError("Quantity must be > 0")

    record = {
        "user_id": user_id,
        "food_id": food_id,
        "food_name": food_name,
        "quantity": quantity,
        "date": date_str,
        "ts": datetime.utcnow().isoformat() + "Z",
    }

    path = _intake_path(app, user_id)
    logs = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            logs = json.load(f) or []

    logs.append(record)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return record


def _period_range(period: str):
    today = datetime.today().date()
    period = (period or "weekly").lower()

    if period == "weekly":
        start = today - timedelta(days=6)   # last 7 days incl today
    elif period == "monthly":
        start = today - timedelta(days=29)  # last 30 days incl today
    else:
        start = today - timedelta(days=6)

    return start, today


def get_summary(app, user_id: str, period: str = "weekly") -> dict:
    """
    Build totals + daily averages for the given period (weekly/monthly),
    using food nutrient values from SL_Food_Nutrition_Master.csv.

    Returns TWO averages:
    - daily_average_logged_days: totals / days_logged
    - daily_average_over_period: totals / 7 or totals / 30  ✅ (fix weekly vs monthly display)
    """
    user_id = (user_id or "demo").strip() or "demo"
    period = (period or "weekly").lower()

    start, end = _period_range(period)

    path = _intake_path(app, user_id)
    logs = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            logs = json.load(f) or []

    # Load food dataset for nutrient lookup
    food_df, _, _ = get_datasets(app)

    # Build fast lookup maps
    by_id = {}
    if "food_id" in food_df.columns:
        for _, r in food_df.iterrows():
            by_id[str(r.get("food_id", "")).strip()] = r

    by_name = {str(r.get("food_name", "")).strip(): r for _, r in food_df.iterrows()}

    nutrient_cols = [
        "energy_kcal",
        "protein_g",
        "fat_g",
        "carbohydrate_g",
        "fiber_g",
        "sugar_g",
        "calcium_mg",
        "iron_mg",
        "zinc_mg",
        "magnesium_mg",
        "potassium_mg",
        "sodium_mg",
        "vitamin_c_mg",
        "vitamin_a_ug",
        "vitamin_d_ug",
        "vitamin_b12_ug",
        "folate_ug",
    ]

    totals = {k: 0.0 for k in nutrient_cols}
    days_logged = set()
    used_logs = 0

    for log in logs:
        date_str = log.get("date")
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            continue

        if d < start or d > end:
            continue

        days_logged.add(d.isoformat())
        used_logs += 1

        fid = str(log.get("food_id") or "").strip()
        fname = str(log.get("food_name") or "").strip()
        qty = float(log.get("quantity") or 1.0)

        row = None
        if fid and fid in by_id:
            row = by_id[fid]
        elif fname and fname in by_name:
            row = by_name[fname]

        if row is None:
            continue

        for k in nutrient_cols:
            if k not in row or str(row[k]) == "nan":
                continue
            try:
                totals[k] += float(row[k]) * qty
            except Exception:
                pass

    totals = {k: round(v, 4) for k, v in totals.items()}

    # ✅ Average by logged days
    logged_day_count = max(1, len(days_logged))
    daily_average_logged_days = {k: round(v / logged_day_count, 4) for k, v in totals.items()}

    # ✅ Average by full period length (7 or 30)
    period_days = 7 if period == "weekly" else 30 if period == "monthly" else 7
    daily_average_over_period = {k: round(v / period_days, 4) for k, v in totals.items()}

    return {
        "user_id": user_id,
        "period": period,
        "date_start": start.isoformat(),
        "date_end": end.isoformat(),
        "days_logged": len(days_logged),
        "logs_used": used_logs,
        "period_days": period_days,
        "totals": totals,
        "daily_average_logged_days": daily_average_logged_days,
        "daily_average_over_period": daily_average_over_period,
        # keep old key for backward compatibility (uses logged days)
        "daily_average": daily_average_logged_days,
    }
