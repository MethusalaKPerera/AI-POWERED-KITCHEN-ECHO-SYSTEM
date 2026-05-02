import os
import json
import joblib
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")

OVERALL_MODEL_PATH = os.path.join(MODEL_DIR, "deficiency_risk_model.pkl")
OVERALL_ENCODER_PATH = os.path.join(MODEL_DIR, "risk_label_encoder.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "deficiency_model_features.json")

NUTRIENT_MODELS = {
    "energy": {
        "model": os.path.join(MODEL_DIR, "energy_risk_model.pkl"),
        "encoder": os.path.join(MODEL_DIR, "energy_risk_encoder.pkl"),
    },
    "protein": {
        "model": os.path.join(MODEL_DIR, "protein_risk_model.pkl"),
        "encoder": os.path.join(MODEL_DIR, "protein_risk_encoder.pkl"),
    },
    "calcium": {
        "model": os.path.join(MODEL_DIR, "calcium_risk_model.pkl"),
        "encoder": os.path.join(MODEL_DIR, "calcium_risk_encoder.pkl"),
    },
    "iron": {
        "model": os.path.join(MODEL_DIR, "iron_risk_model.pkl"),
        "encoder": os.path.join(MODEL_DIR, "iron_risk_encoder.pkl"),
    },
}

_overall_model = None
_overall_encoder = None
_features = None
_nutrient_assets = {}


def safe_ratio(actual, required):
    try:
        actual = float(actual or 0)
        required = float(required or 0)

        if required <= 0:
            return 0

        return actual / required
    except Exception:
        return 0


def load_overall_assets():
    global _overall_model, _overall_encoder, _features

    if _overall_model is None:
        _overall_model = joblib.load(OVERALL_MODEL_PATH)

    if _overall_encoder is None:
        _overall_encoder = joblib.load(OVERALL_ENCODER_PATH)

    if _features is None:
        with open(FEATURES_PATH, "r", encoding="utf-8") as f:
            _features = json.load(f)

    return _overall_model, _overall_encoder, _features


def load_nutrient_assets():
    global _nutrient_assets

    if _nutrient_assets:
        return _nutrient_assets

    for nutrient, paths in NUTRIENT_MODELS.items():
        _nutrient_assets[nutrient] = {
            "model": joblib.load(paths["model"]),
            "encoder": joblib.load(paths["encoder"]),
        }

    return _nutrient_assets


def build_feature_row(user_features):
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

    return row


def predict_with_model(model, encoder, input_df):
    prediction_encoded = model.predict(input_df)[0]
    prediction_label = encoder.inverse_transform([prediction_encoded])[0]

    confidence_scores = None

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(input_df)[0]
        confidence_scores = {
            label: round(float(prob), 4)
            for label, prob in zip(encoder.classes_, proba)
        }

    return prediction_label, confidence_scores


def get_top_confidence(confidence_scores):
    if not confidence_scores:
        return None

    return max(confidence_scores.values())


def build_ml_explanation(overall_risk, nutrient_breakdown):
    high_items = []
    medium_items = []

    for nutrient, data in nutrient_breakdown.items():
        level = str(data.get("risk_level", "")).upper()

        if level == "HIGH":
            high_items.append(nutrient)
        elif level == "MEDIUM":
            medium_items.append(nutrient)

    if high_items:
        causes = ", ".join(high_items)
        return f"{overall_risk} risk predicted mainly because the ML nutrient models detected high concern in {causes}."

    if medium_items:
        causes = ", ".join(medium_items)
        return f"{overall_risk} risk predicted because the ML nutrient models detected moderate concern in {causes}."

    return f"{overall_risk} risk predicted because the nutrient intake pattern is close to the required level."


def build_recommendations(nutrient_breakdown):
    recommendations = []

    FOOD_MAP = {
        "energy": "Increase calorie-dense foods such as rice, whole grains, nuts, and healthy oils.",
        "protein": "Increase protein-rich foods such as eggs, fish, chicken, lentils, and dairy products.",
        "calcium": "Increase calcium-rich foods such as milk, yoghurt, cheese, and small fish.",
        "iron": "Increase iron-rich foods such as spinach, lentils, red meat, eggs, and fish.",
    }

    for nutrient, data in nutrient_breakdown.items():
        level = str(data.get("risk_level", "")).upper()

        if level == "HIGH":
            recommendations.append({
                "nutrient": nutrient,
                "priority": "HIGH",
                "advice": FOOD_MAP.get(nutrient)
            })

        elif level == "MEDIUM":
            recommendations.append({
                "nutrient": nutrient,
                "priority": "MEDIUM",
                "advice": f"Consider improving {nutrient} intake slightly with balanced food choices."
            })

    return recommendations

def predict_deficiency_risk(user_features):
    overall_model, overall_encoder, features = load_overall_assets()
    nutrient_assets = load_nutrient_assets()

    row = build_feature_row(user_features)

    input_df = pd.DataFrame([row])

    for feature in features:
        if feature not in input_df.columns:
            input_df[feature] = 0

    input_df = input_df[features]

    overall_risk, overall_confidence_scores = predict_with_model(
        overall_model,
        overall_encoder,
        input_df,
    )

    nutrient_breakdown = {}

    for nutrient, assets in nutrient_assets.items():
        nutrient_risk, nutrient_confidence_scores = predict_with_model(
            assets["model"],
            assets["encoder"],
            input_df,
        )

        ratio_key = f"{nutrient}_ratio"

        nutrient_breakdown[nutrient] = {
            "risk_level": nutrient_risk,
            "confidence_scores": nutrient_confidence_scores,
            "confidence": get_top_confidence(nutrient_confidence_scores),
            "ratio_used": round(float(row.get(ratio_key, 0) or 0), 3),
        }

    main_causes = [
        nutrient
        for nutrient, data in nutrient_breakdown.items()
        if str(data.get("risk_level", "")).upper() == "HIGH"
    ]

    explanation = build_ml_explanation(overall_risk, nutrient_breakdown)
    recommendations = build_recommendations(nutrient_breakdown)

    return {
    "risk_level": overall_risk,
    "confidence_scores": overall_confidence_scores,
    "confidence": get_top_confidence(overall_confidence_scores),
    "nutrient_breakdown": nutrient_breakdown,
    "main_causes": main_causes,
    "explanation": explanation,
    "recommendations": recommendations,
    "features_used": row,
    "model_type": "Overall + nutrient-specific ML models",
}

    