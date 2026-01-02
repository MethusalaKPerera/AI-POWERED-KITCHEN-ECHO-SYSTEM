# backend/NutritionGuidance/services/profile_store.py

import json
import os

DEFAULT_PROFILE = {
    "user_id": "demo",
    "age": 22,
    "group": "male",        # male / female / pregnant / lactating
    "conditions": []        # list of strings
}

def _profile_path(app, user_id: str) -> str:
    store_dir = app.config.get("STORE_DIR") or os.path.join(os.getcwd(), "store")
    os.makedirs(store_dir, exist_ok=True)
    return os.path.join(store_dir, f"profile_{user_id}.json")

def get_profile(app, user_id: str) -> dict:
    user_id = (user_id or "demo").strip() or "demo"
    path = _profile_path(app, user_id)

    if not os.path.exists(path):
        p = dict(DEFAULT_PROFILE)
        p["user_id"] = user_id
        return p

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f) or {}

    # Ensure required keys exist
    profile = dict(DEFAULT_PROFILE)
    profile.update(data)
    profile["user_id"] = user_id

    # Clean types
    try:
        profile["age"] = int(profile.get("age") or 0)
    except Exception:
        profile["age"] = 0

    profile["group"] = str(profile.get("group") or "male").strip().lower()
    if profile["group"] not in ["male", "female", "pregnant", "lactating"]:
        profile["group"] = "male"

    conds = profile.get("conditions")
    if not isinstance(conds, list):
        conds = []
    profile["conditions"] = [str(c).strip().lower() for c in conds if str(c).strip()]

    return profile

def save_profile(app, user_id: str, profile: dict) -> dict:
    user_id = (user_id or "demo").strip() or "demo"

    # Start with a clean structure
    clean = {
        "user_id": user_id,
        "age": int(profile.get("age") or 0),
        "group": str(profile.get("group") or "male").strip().lower(),
        "conditions": profile.get("conditions") or []
    }

    if clean["group"] not in ["male", "female", "pregnant", "lactating"]:
        clean["group"] = "male"

    if not isinstance(clean["conditions"], list):
        clean["conditions"] = []

    clean["conditions"] = [str(c).strip().lower() for c in clean["conditions"] if str(c).strip()]

    path = _profile_path(app, user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)

    return clean
