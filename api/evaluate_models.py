import os
import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")


import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

BASE_DIR = Path("C:/Users/moizk/Desktop/Coding/RADIANT/CircuitSaver/api")
OUTPUT_DIR = BASE_DIR / "model_eval_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MASTER_DATASET_PATH = Path("data/processed/master_dataset.csv")
REBOUND_DATA_PATH = Path("data/synthetic/rebound_training_data.csv")
BASELINE_MODEL_DIR = Path("app/services/baseline_predictor/saved_models")
ANTI_REBOUND_MODEL_PATH = Path("app/services/optimizer/saved_models/anti_rebound_model.pkl")

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
BASE_TARGET_COLUMN = "load_kw"
REGIONS = ["Austin_TX", "London_UK"]

ANTI_FEATURE_COLUMNS = [
    "appliance_kw",
    "transformer_rated_kva",
    "transformer_loading_percent",
    "num_simultaneous_restarts",
    "flexibility_score",
    "carbon_priority_weight",
    "cost_priority_weight",
]
ANTI_TARGET_COLUMN = "stagger_label"


def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def clean_filename(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "_")


def load_and_clean_baseline(region: str):
    df = pd.read_csv(MASTER_DATASET_PATH)
    df = df[df["region"] == region].copy()

    df = df.dropna(
        subset=[
            "temperature_c",
            "humidity_pct",
            "hour",
            "day_of_week",
            "is_weekend",
            "month",
            "flexibility_score",
            "household_type",
            BASE_TARGET_COLUMN,
        ]
    )
    df = df[df[BASE_TARGET_COLUMN] > -5]

    household_avg = df.groupby("household_id")[BASE_TARGET_COLUMN].transform("mean")
    df["household_avg_load"] = household_avg

    household_type_dummies = pd.get_dummies(df["household_type"], prefix="htype")
    df = pd.concat([df, household_type_dummies], axis=1)

    feature_columns = BASE_FEATURE_COLUMNS + list(household_type_dummies.columns)
    return df, feature_columns


def evaluate_baseline_region(region: str):
    df, feature_columns = load_and_clean_baseline(region)
    if len(df) < 50:
        return {
            "region": region,
            "rows": len(df),
            "status": "skipped",
            "reason": "not enough rows",
        }

    X = df[feature_columns]
    y = df[BASE_TARGET_COLUMN]

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
    rmse = mean_squared_error(y_test, preds) ** 0.5
    r2 = r2_score(y_test, preds)

    feature_importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    pred_df = pd.DataFrame({
        "actual_load_kw": y_test.values,
        "predicted_load_kw": preds,
    })
    pred_df.to_csv(OUTPUT_DIR / f"baseline_predictions_{clean_filename(region)}.csv", index=False)
    feature_importance.to_csv(OUTPUT_DIR / f"baseline_feature_importance_{clean_filename(region)}.csv", index=False)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, preds, alpha=0.35)
    min_val = min(float(np.min(y_test)), float(np.min(preds)))
    max_val = max(float(np.max(y_test)), float(np.max(preds)))
    plt.plot([min_val, max_val], [min_val, max_val], linestyle="--", linewidth=2)
    plt.xlabel("Actual load (kW)")
    plt.ylabel("Predicted load (kW)")
    plt.title(f"Baseline model: actual vs predicted — {region}")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"baseline_actual_vs_predicted_{clean_filename(region)}.png", dpi=200)
    plt.close()

    top_features = feature_importance.head(10).sort_values("importance")
    plt.figure(figsize=(9, 6))
    plt.barh(top_features["feature"], top_features["importance"])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title(f"Baseline model feature importance — {region}")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"baseline_feature_importance_{clean_filename(region)}.png", dpi=200)
    plt.close()

    return {
        "region": region,
        "rows": int(len(df)),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "status": "ok",
    }


def evaluate_all_baseline():
    results = []
    for region in REGIONS:
        results.append(evaluate_baseline_region(region))

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_DIR / "baseline_metrics_summary.csv", index=False)

    ok_df = results_df[results_df["status"] == "ok"].copy()
    if not ok_df.empty:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].bar(ok_df["region"], ok_df["mae"])
        axes[0].set_title("Baseline MAE by region")
        axes[0].set_ylabel("MAE (kW)")
        axes[0].set_xlabel("Region")

        axes[1].bar(ok_df["region"], ok_df["r2"])
        axes[1].set_title("Baseline R² by region")
        axes[1].set_ylabel("R²")
        axes[1].set_xlabel("Region")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "baseline_metrics_comparison.png", dpi=200)
        plt.close()

    return results


def evaluate_anti_rebound():
    df = pd.read_csv(REBOUND_DATA_PATH)
    df = df.dropna(subset=ANTI_FEATURE_COLUMNS + [ANTI_TARGET_COLUMN]).copy()

    X = df[ANTI_FEATURE_COLUMNS]
    y = df[ANTI_TARGET_COLUMN]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
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
    probs = model.predict_proba(X_test)
    accuracy = accuracy_score(y_test, preds)
    report = classification_report(
        y_test,
        preds,
        target_names=label_encoder.classes_,
        output_dict=True,
        zero_division=0,
    )

    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv(OUTPUT_DIR / "anti_rebound_classification_report.csv")

    cm = confusion_matrix(y_test, preds)
    cm_df = pd.DataFrame(cm, index=label_encoder.classes_, columns=label_encoder.classes_)
    cm_df.to_csv(OUTPUT_DIR / "anti_rebound_confusion_matrix.csv")

    feature_importance = pd.DataFrame(
        {
            "feature": ANTI_FEATURE_COLUMNS,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    feature_importance.to_csv(OUTPUT_DIR / "anti_rebound_feature_importance.csv", index=False)

    test_results = X_test.copy()
    test_results["actual_label"] = label_encoder.inverse_transform(y_test)
    test_results["predicted_label"] = label_encoder.inverse_transform(preds)
    test_results["prediction_confidence"] = probs.max(axis=1)
    test_results.to_csv(OUTPUT_DIR / "anti_rebound_test_predictions.csv", index=False)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Greens")
    plt.xlabel("Predicted label")
    plt.ylabel("Actual label")
    plt.title("Anti-rebound confusion matrix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "anti_rebound_confusion_matrix.png", dpi=200)
    plt.close()

    top_features = feature_importance.sort_values("importance").tail(10)
    plt.figure(figsize=(9, 6))
    plt.barh(top_features["feature"], top_features["importance"])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Anti-rebound feature importance")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "anti_rebound_feature_importance.png", dpi=200)
    plt.close()

    label_counts = pd.Series(label_encoder.inverse_transform(y_test)).value_counts().sort_index()
    plt.figure(figsize=(8, 5))
    plt.bar(label_counts.index, label_counts.values)
    plt.xlabel("Delay class")
    plt.ylabel("Test rows")
    plt.title("Anti-rebound test-set class mix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "anti_rebound_class_distribution.png", dpi=200)
    plt.close()

    summary = {
        "rows": int(len(df)),
        "accuracy": float(accuracy),
        "labels": list(label_encoder.classes_),
    }
    save_json(summary, OUTPUT_DIR / "anti_rebound_summary.json")
    return summary, report_df


def try_model_loads():
    model_status = {}
    for region in REGIONS:
        model_path = BASELINE_MODEL_DIR / f"baseline_model_{region}.pkl"
        model_status[f"baseline_{region}"] = model_path.exists()
        if model_path.exists():
            try:
                joblib.load(model_path)
                model_status[f"baseline_{region}_loadable"] = True
            except Exception:
                model_status[f"baseline_{region}_loadable"] = False

    model_status["anti_rebound_model_exists"] = ANTI_REBOUND_MODEL_PATH.exists()
    if ANTI_REBOUND_MODEL_PATH.exists():
        try:
            joblib.load(ANTI_REBOUND_MODEL_PATH)
            model_status["anti_rebound_model_loadable"] = True
        except Exception:
            model_status["anti_rebound_model_loadable"] = False

    save_json(model_status, OUTPUT_DIR / "saved_model_status.json")
    return model_status


def print_baseline_results(results):
    print("\n=== Baseline Predictor Results ===")
    for r in results:
        if r.get("status") != "ok":
            print(f"{r['region']}: skipped ({r.get('reason', 'unknown reason')})")
            continue
        print(
            f"{r['region']} | rows={r['rows']} | "
            f"MAE={r['mae']:.4f} kW | RMSE={r['rmse']:.4f} kW | R2={r['r2']:.4f}"
        )


def print_anti_results(summary, report_df):
    print("\n=== Anti-Rebound Classifier Results ===")
    print(f"Rows used: {summary['rows']}")
    print(f"Accuracy: {summary['accuracy']:.4f}")
    print("\nClassification report:")
    print(report_df.round(4).to_string())


def main():
    print("Starting model evaluation...")
    print(f"Master dataset path: {MASTER_DATASET_PATH}")
    print(f"Rebound dataset path: {REBOUND_DATA_PATH}")

    model_status = try_model_loads()
    print("\n=== Saved Model Status ===")
    print(json.dumps(model_status, indent=2))

    baseline_results = evaluate_all_baseline()
    anti_summary, anti_report = evaluate_anti_rebound()

    print_baseline_results(baseline_results)
    print_anti_results(anti_summary, anti_report)

    combined_summary = {
        "baseline": baseline_results,
        "anti_rebound": anti_summary,
        "saved_models": model_status,
    }
    save_json(combined_summary, OUTPUT_DIR / "evaluation_summary.json")

    print("\nArtifacts written to:", OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    main()