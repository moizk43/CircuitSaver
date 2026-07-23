"""
anti_rebound.py
Anti-Rebound Classifier: predicts a safe restart stagger delay class
for each household's appliance after a load-shed event ends, to avoid
a rebound demand spike on the shared transformer.

Contains both training and prediction logic.
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

TRAINING_DATA_PATH = "data/synthetic/rebound_training_data.csv"
MODEL_OUTPUT_DIR = "app/services/optimizer/saved_models"
MODEL_PATH = os.path.join(MODEL_OUTPUT_DIR, "anti_rebound_model.pkl")

FEATURE_COLUMNS = [
    "appliance_kw",
    "transformer_rated_kva",
    "transformer_loading_percent",
    "num_simultaneous_restarts",
    "flexibility_score",
    "carbon_priority_weight",
    "cost_priority_weight",
]
TARGET_COLUMN = "stagger_label"

STAGGER_DELAY_MINUTES = {
    "immediate": 0,
    "short_delay": 10,
    "medium_delay": 22,
    "long_delay": 45,
}

_cached_model_bundle = None


def train_model():
    if not os.path.exists(TRAINING_DATA_PATH):
        raise FileNotFoundError(
            f"Training data not found at {TRAINING_DATA_PATH}. "
            f"Run generate_rebound_training_data.py first."
        )

    df = pd.read_csv(TRAINING_DATA_PATH)
    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)

    print(f"Rows used: {len(df)}")
    print(f"Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, preds, target_names=label_encoder.classes_))

    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    joblib.dump({
        "model": model,
        "label_encoder": label_encoder,
        "feature_columns": FEATURE_COLUMNS,
    }, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")

    return {"rows": len(df), "accuracy": accuracy}


def load_model():
    global _cached_model_bundle
    if _cached_model_bundle is not None:
        return _cached_model_bundle

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"No trained anti-rebound model found at {MODEL_PATH}. Run train_model() first."
        )

    _cached_model_bundle = joblib.load(MODEL_PATH)
    return _cached_model_bundle


def predict_stagger(features: dict):
    bundle = load_model()
    model = bundle["model"]
    label_encoder = bundle["label_encoder"]
    feature_columns = bundle["feature_columns"]

    missing = [c for c in feature_columns if c not in features]
    if missing:
        raise ValueError(f"Missing required features for prediction: {missing}")

    X = pd.DataFrame([features])[feature_columns]
    predicted_class_idx = model.predict(X)[0]
    predicted_label = label_encoder.inverse_transform([predicted_class_idx])[0]

    probabilities = model.predict_proba(X)[0]
    confidence = float(max(probabilities))

    return {
        "stagger_label": predicted_label,
        "recommended_delay_minutes": STAGGER_DELAY_MINUTES[predicted_label],
        "confidence": round(confidence, 3),
    }


def plan_restart_schedule(households_restarting: list):
    schedule = []
    for household in households_restarting:
        prediction = predict_stagger(household["features"])
        schedule.append({
            "user_id": household["user_id"],
            "appliance": household["features"].get("appliance", "unknown"),
            **prediction,
        })

    schedule = sorted(schedule, key=lambda x: x["recommended_delay_minutes"])
    return schedule


if __name__ == "__main__":
    print("=== Training Anti-Rebound Classifier ===")
    train_model()

    print("\n=== Example Prediction ===")
    example_features = {
        "appliance_kw": 7.0,
        "transformer_rated_kva": 25,
        "transformer_loading_percent": 87.8,
        "num_simultaneous_restarts": 6,
        "flexibility_score": 0.45,
        "carbon_priority_weight": 0.6,
        "cost_priority_weight": 0.4,
    }
    result = predict_stagger(example_features)
    print(result)