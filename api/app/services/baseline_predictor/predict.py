"""
predict.py
Loads the correct region-specific Baseline Predictor model and generates
a baseline load prediction for a given household's current conditions.
"""

import os
import joblib
import pandas as pd

MODEL_DIR = "app/services/baseline_predictor/saved_models"

_loaded_models = {}


def load_model(region):
    if region in _loaded_models:
        return _loaded_models[region]

    model_path = os.path.join(MODEL_DIR, f"baseline_model_{region}.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No trained model found for region '{region}' at {model_path}. "
            f"Run train.py first."
        )

    bundle = joblib.load(model_path)
    _loaded_models[region] = bundle
    return bundle


def predict_baseline(region, household_id, features: dict):
    bundle = load_model(region)
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]
    household_avg_lookup = bundle["household_avg_lookup"]
    global_avg_load = bundle["global_avg_load"]

    features = dict(features)
    features["household_avg_load"] = household_avg_lookup.get(household_id, global_avg_load)

    household_type = features.pop("household_type", None)
    for col in feature_columns:
        if col.startswith("htype_"):
            features[col] = 1 if col == f"htype_{household_type}" else 0

    missing = [c for c in feature_columns if c not in features]
    if missing:
        raise ValueError(f"Missing required features for prediction: {missing}")

    X = pd.DataFrame([features])[feature_columns]
    prediction = model.predict(X)[0]
    prediction = max(0.0, float(prediction))

    return round(prediction, 4)


if __name__ == "__main__":
    example_features = {
        "temperature_c": 32.0,
        "humidity_pct": 45.0,
        "hour": 18,
        "day_of_week": 2,
        "is_weekend": 0,
        "month": 7,
        "flexibility_score": 0.5,
        "household_type": "family_of_4",
    }

    result = predict_baseline("Austin_TX", household_id="some_household_id", features=example_features)
    print(f"Predicted baseline load: {result} kW")