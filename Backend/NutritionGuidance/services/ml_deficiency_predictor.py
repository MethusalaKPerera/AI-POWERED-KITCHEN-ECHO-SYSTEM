import os
import json
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")

MODEL_PATH = os.path.join(MODEL_DIR, "deficiency_risk_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "risk_label_encoder.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "deficiency_model_features.json")


_model = None
_encoder = None
_features = None


def load_ml_assets():
    global _model, _encoder, _features

    if _model is None:
        _model = joblib.load(MODEL_PATH)

    if _encoder is None:
        _encoder = joblib.load(ENCODER_PATH)

    if _features is None:
        with open(FEATURES_PATH, "r", encoding="utf-8") as f:
            _features = json.load(f)

    return _model, _encoder, _features


def safe_ratio(actual, required):
    try:
        actual = float(actual or 0)
        required = float(required or 0)
        if required <= 0:
            return 0
        return actual / required
    except Exception:
        return 0


def predict_deficiency_risk(user_features):
    """
    Predicts LOW / MEDIUM / HIGH deficiency risk using the trained ML model.
    """

    model, encoder, features = load_ml_assets()

    row = {
        "age": user_features.get("age", 0),
        "gender_code": user_features.get("gender_code", 2),
        "condition_flag": user_features.get("condition_flag", 0),

        "energy_intake": user_features.get("energy_intake", 0),
        "protein_intake": user_features.get("protein_intake", 0),
        "calcium_intake": user_features.get("calcium_intake", 0),
        "iron_intake": user_features.get("iron_intake", 0),

        "required_energy": user_features.get("required_energy", 0),
        "required_protein": user_features.get("required_protein", 0),
        "required_calcium": user_features.get("required_calcium", 0),
        "required_iron": user_features.get("required_iron", 0),
    }

    row["energy_ratio"] = safe_ratio(row["energy_intake"], row["required_energy"])
    row["protein_ratio"] = safe_ratio(row["protein_intake"], row["required_protein"])
    row["calcium_ratio"] = safe_ratio(row["calcium_intake"], row["required_calcium"])
    row["iron_ratio"] = safe_ratio(row["iron_intake"], row["required_iron"])

    input_df = pd.DataFrame([row])

    for feature in features:
        if feature not in input_df.columns:
            input_df[feature] = 0

    input_df = input_df[features]

    prediction_encoded = model.predict(input_df)[0]
    prediction_label = encoder.inverse_transform([prediction_encoded])[0]

    probabilities = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(input_df)[0]
        probabilities = {
            label: round(float(prob), 4)
            for label, prob in zip(encoder.classes_, proba)
        }

    return {
        "risk_level": prediction_label,
        "confidence_scores": probabilities,
        "features_used": row,
    }