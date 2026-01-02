import os
import joblib

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "deficiency_risk_model.pkl"
)

_model = None


def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_risk(age, avg):
    """
    Predict deficiency risk using ML.
    avg = daily_average_over_period
    """
    model = _load_model()

    X = [[
        age,
        avg.get("energy_kcal", 0),
        avg.get("protein_g", 0),
        avg.get("calcium_mg", 0),
        avg.get("iron_mg", 0),
    ]]

    return model.predict(X)[0]
