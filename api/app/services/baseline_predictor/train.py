"""
train.py
Trains separate Baseline Predictor models per region (Austin_TX, London_UK)
using the master dataset. Each region gets its own saved model file.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

MASTER_DATASET_PATH = "data/processed/master_dataset.csv"
MODEL_OUTPUT_DIR = "app/services/baseline_predictor/saved_models"

BASE_FEATURE_COLUMNS = [
    "temperature_c",
    "humidity_pct",
    "hour",
    "day_of_week",
    "is_weekend",
    "month",
    "flexibility_score",
    "household_avg_load",
]
TARGET_COLUMN = "load_kw"
REGIONS = ["Austin_TX", "London_UK"]


def load_and_clean(region):
    df = pd.read_csv(MASTER_DATASET_PATH)
    df = df[df["region"] == region].copy()

    df = df.dropna(subset=["temperature_c", "humidity_pct", "hour", "day_of_week",
                            "is_weekend", "month", "flexibility_score",
                            "household_type", TARGET_COLUMN])
    df = df[df[TARGET_COLUMN] > -5]

    household_avg = df.groupby("household_id")[TARGET_COLUMN].transform("mean")
    df["household_avg_load"] = household_avg

    household_type_dummies = pd.get_dummies(df["household_type"], prefix="htype")
    df = pd.concat([df, household_type_dummies], axis=1)

    feature_columns = BASE_FEATURE_COLUMNS + list(household_type_dummies.columns)
    return df, feature_columns


def train_region_model(region):
    print(f"\n--- Training model for {region} ---")
    df, feature_columns = load_and_clean(region)

    if len(df) < 50:
        print(f"Skipping {region}: not enough rows ({len(df)}) to train reliably.")
        return None

    X = df[feature_columns]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=14,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"{region} — rows used: {len(df)}, MAE: {mae:.4f} kW, R2: {r2:.4f}")

    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_OUTPUT_DIR, f"baseline_model_{region}.pkl")
    joblib.dump({
        "model": model,
        "feature_columns": feature_columns,
        "household_avg_lookup": df.groupby("household_id")[TARGET_COLUMN].mean().to_dict(),
        "global_avg_load": df[TARGET_COLUMN].mean(),
    }, model_path)
    print(f"Saved model to {model_path}")

    return {"region": region, "rows": len(df), "mae": mae, "r2": r2}


def train_all_regions():
    results = []
    for region in REGIONS:
        result = train_region_model(region)
        if result:
            results.append(result)

    print("\n=== Training Summary ===")
    for r in results:
        print(r)

    return results


if __name__ == "__main__":
    train_all_regions()