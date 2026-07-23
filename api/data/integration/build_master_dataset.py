"""
build_master_dataset.py
Fuses Pecan Street, London consumption, weather, WattTime carbon data,
synthetic user profiles, and synthetic transformer topology into one
master feature table for the Baseline Predictor, Capacity Allocator,
and Anti-Rebound Classifier.

Output: data/processed/master_dataset.csv
"""

import os
import pandas as pd
import numpy as np

RAW_DIR = "data/raw"
SYNTHETIC_DIR = "data/synthetic"
PROCESSED_DIR = "data/processed"
RESAMPLE_FREQ = "15min"


def require_columns(df, required, name):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"[{name}] Missing expected columns: {missing}. "
            f"Available columns: {list(df.columns)}. "
            f"Update the column-mapping constants at the top of this script."
        )


def load_pecan_street():
    path = os.path.join(RAW_DIR, "pecan_street_wide.csv")
    df = pd.read_csv(path)

    time_col = next((c for c in df.columns if c.lower() in ["local_15min", "timestamp", "datetime", "time"]), None)
    if time_col is None:
        raise ValueError(f"[pecan_street] Could not find a timestamp column. Columns: {list(df.columns)}")

    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col]).rename(columns={time_col: "timestamp"})

    id_cols = ["timestamp"]
    household_cols = [c for c in df.columns if c not in id_cols and c.lower() not in ["dataid", "grid"]]

    melted = df.melt(id_vars="timestamp", value_vars=household_cols,
                      var_name="pecan_household_id", value_name="load_kw")
    melted["load_kw"] = pd.to_numeric(melted["load_kw"], errors="coerce")
    melted = melted.dropna(subset=["load_kw"])
    melted["region"] = "Austin_TX"

    melted = (
        melted.set_index("timestamp")
        .groupby("pecan_household_id")
        .resample(RESAMPLE_FREQ)
        .agg({"load_kw": "mean", "region": "first"})
        .reset_index()
    )
    return melted


def load_london():
    path = os.path.join(RAW_DIR, "london_daily_consumption.csv")
    df = pd.read_csv(path)

    time_col = next((c for c in df.columns if c.lower() in ["day", "date", "timestamp", "datetime"]), None)
    id_col = next((c for c in df.columns if "lclid" in c.lower() or "household" in c.lower() or c.lower() == "id"), None)
    load_col = next((c for c in df.columns if "kwh" in c.lower() or "consumption" in c.lower() or "energy" in c.lower()), None)

    if not all([time_col, id_col, load_col]):
        raise ValueError(
            f"[london] Could not auto-detect columns. time_col={time_col}, id_col={id_col}, load_col={load_col}. "
            f"Available columns: {list(df.columns)}"
        )

    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col])
    df = df.rename(columns={time_col: "timestamp", id_col: "london_household_id", load_col: "load_kw"})
    df["load_kw"] = pd.to_numeric(df["load_kw"], errors="coerce")
    df["region"] = "London_UK"

    return df[["timestamp", "london_household_id", "load_kw", "region"]]


def load_weather():
    austin_path = os.path.join(RAW_DIR, "weather_austin.csv")
    london_path = os.path.join(RAW_DIR, "weather_london.csv")

    frames = []
    for path, region in [(austin_path, "Austin_TX"), (london_path, "London_UK")]:
        df = pd.read_csv(path)
        time_col = next((c for c in df.columns if c.lower() in ["time", "timestamp", "date", "datetime"]), None)
        temp_col = next((c for c in df.columns if "temp" in c.lower()), None)

        if not all([time_col, temp_col]):
            raise ValueError(f"[weather:{region}] Could not detect time/temp columns. Columns: {list(df.columns)}")

        df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
        df = df.dropna(subset=[time_col]).rename(columns={time_col: "timestamp", temp_col: "temperature_c"})
        df["region"] = region

        keep_cols = ["timestamp", "region", "temperature_c"]
        humidity_col = next((c for c in df.columns if "humid" in c.lower()), None)
        if humidity_col:
            df = df.rename(columns={humidity_col: "humidity_pct"})
            keep_cols.append("humidity_pct")

        df = df.set_index("timestamp").resample(RESAMPLE_FREQ).ffill().reset_index()
        frames.append(df[keep_cols + (["humidity_pct"] if "humidity_pct" in df.columns else [])])

    return pd.concat(frames, ignore_index=True)


def load_carbon():
    path = os.path.join(RAW_DIR, "watttime_carbon_cleaned.csv")
    df = pd.read_csv(path)

    time_col = next((c for c in df.columns if "point_time" in c.lower() or "timestamp" in c.lower()), None)
    value_col = next((c for c in df.columns if c.lower() == "value" or "co2" in c.lower() or "moer" in c.lower()), None)

    if not all([time_col, value_col]):
        raise ValueError(f"[watttime] Could not detect columns. Columns: {list(df.columns)}")

    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col]).rename(columns={time_col: "timestamp", value_col: "co2_moer"})
    df["grid_region"] = "CAISO_NORTH"

    df = df.set_index("timestamp").resample(RESAMPLE_FREQ)["co2_moer"].mean().reset_index()
    df["grid_region"] = "CAISO_NORTH"
    return df


def load_synthetic_users():
    path = os.path.join(SYNTHETIC_DIR, "user_profiles.csv")
    df = pd.read_csv(path)
    require_columns(df, ["user_id", "region", "household_type", "flexibility_score",
                          "carbon_priority_weight", "cost_priority_weight"], "user_profiles")
    return df


def load_synthetic_transformers():
    path = os.path.join(SYNTHETIC_DIR, "transformer_topology.csv")
    df = pd.read_csv(path)
    require_columns(df, ["transformer_id", "region", "rated_kva", "connected_user_ids",
                          "loading_percent", "status"], "transformer_topology")

    exploded_rows = []
    for _, row in df.iterrows():
        user_ids = str(row["connected_user_ids"]).split(",")
        for uid in user_ids:
            exploded_rows.append({
                "user_id": uid.strip(),
                "transformer_id": row["transformer_id"],
                "rated_kva": row["rated_kva"],
                "loading_percent": row["loading_percent"],
                "transformer_status": row["status"],
            })
    return pd.DataFrame(exploded_rows)


def assign_synthetic_context(household_ids, region, users_df, transformers_exploded):
    region_users = users_df[users_df["region"] == region].reset_index(drop=True)
    if len(region_users) == 0:
        raise ValueError(f"No synthetic users found for region: {region}")

    n = len(household_ids)
    repeated = pd.concat([region_users] * (n // len(region_users) + 1), ignore_index=True).iloc[:n]
    repeated = repeated.reset_index(drop=True)
    repeated["household_id"] = household_ids

    merged = repeated.merge(transformers_exploded, on="user_id", how="left")
    return merged


def add_calendar_features(df):
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["month"] = df["timestamp"].dt.month
    return df


def build_master_dataset():
    print("Loading Pecan Street...")
    pecan = load_pecan_street()

    print("Loading London...")
    london = london_df = load_london().rename(columns={"london_household_id": "pecan_household_id"})

    print("Loading weather...")
    weather = load_weather()

    print("Loading synthetic users and transformers...")
    users_df = load_synthetic_users()
    transformers_exploded = load_synthetic_transformers()

    load_df = pd.concat([pecan, london], ignore_index=True)
    load_df = load_df.rename(columns={"pecan_household_id": "household_id"})

    print("Merging weather onto load data...")
    merged = pd.merge_asof(
        load_df.sort_values("timestamp"),
        weather.sort_values("timestamp"),
        on="timestamp",
        by="region",
        direction="nearest",
        tolerance=pd.Timedelta(RESAMPLE_FREQ) * 2,
    )

    print("Assigning synthetic user/transformer context per household...")
    context_frames = []
    for region in merged["region"].unique():
        household_ids = merged.loc[merged["region"] == region, "household_id"].unique()
        context = assign_synthetic_context(household_ids, region, users_df, transformers_exploded)
        context_frames.append(context)
    context_all = pd.concat(context_frames, ignore_index=True)

    context_cols = ["household_id", "user_id", "household_type", "flexibility_score",
                     "carbon_priority_weight", "cost_priority_weight", "transformer_id",
                     "rated_kva", "loading_percent", "transformer_status"]
    merged = merged.merge(context_all[context_cols], on="household_id", how="left")
    merged = merged.loc[:, ~merged.columns.duplicated()]
    merged = add_calendar_features(merged)

    merged = merged.sort_values(["household_id", "timestamp"]).reset_index(drop=True)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DIR, "master_dataset.csv")
    merged.to_csv(out_path, index=False)

    print(f"Master dataset saved to {out_path}")
    print(f"Shape: {merged.shape}")
    print(f"Columns: {list(merged.columns)}")
    return merged


if __name__ == "__main__":
    build_master_dataset()