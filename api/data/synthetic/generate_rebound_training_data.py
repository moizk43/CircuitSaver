"""
generate_rebound_training_data.py
Generates physically-grounded synthetic training labels for the
Anti-Rebound Classifier, based on appliance load relative to transformer
capacity, pre-event transformer stress, and simultaneous restart pool size.

Simulates multiple distinct peak-event scenarios per household-appliance
pair to produce enough training volume and class balance for a reliable
4-class classifier.
"""

import os
import numpy as np
import pandas as pd

np.random.seed(11)

USER_PROFILES_PATH = "data/synthetic/user_profiles.csv"
TRANSFORMER_TOPOLOGY_PATH = "data/synthetic/transformer_topology.csv"
OUTPUT_PATH = "data/synthetic/rebound_training_data.csv"

SCENARIOS_PER_HOUSEHOLD_APPLIANCE = 40

APPLIANCE_TYPICAL_KW = {
    "ev_charger": 7.2,
    "dryer": 3.0,
    "dishwasher": 1.3,
    "washing_machine": 1.0,
    "hvac": 4.0,
    "water_heater": 3.5,
    "pool_pump": 1.5,
}


def parse_appliance_kwh(raw_string):
    result = {}
    if not isinstance(raw_string, str) or raw_string.strip() == "":
        return result
    for pair in raw_string.split(";"):
        if ":" not in pair:
            continue
        appliance, value = pair.split(":")
        try:
            result[appliance.strip()] = float(value.strip())
        except ValueError:
            continue
    return result


def compute_rebound_risk(appliance_kw, rated_kva, loading_percent, num_simultaneous, flexibility_score):
    relative_load = appliance_kw / max(rated_kva, 1.0)
    pre_stress = loading_percent / 100.0
    crowd_factor = np.log1p(num_simultaneous) / np.log1p(10)
    flexibility_buffer = (1.0 - flexibility_score) * 0.3

    risk = (
        0.45 * relative_load
        + 0.30 * pre_stress
        + 0.20 * crowd_factor
        + 0.05 * flexibility_buffer
    )
    return risk


def bucket_risk(risk_score):
    if risk_score < 0.15:
        return "immediate"
    elif risk_score < 0.30:
        return "short_delay"
    elif risk_score < 0.45:
        return "medium_delay"
    else:
        return "long_delay"


def generate_training_rows():
    users = pd.read_csv(USER_PROFILES_PATH)
    transformers = pd.read_csv(TRANSFORMER_TOPOLOGY_PATH)

    users["appliance_kwh_map"] = users["appliance_avg_kwh_per_use"].apply(parse_appliance_kwh)
    users["shiftable_list"] = users["shiftable_appliances"].apply(
        lambda x: [] if pd.isna(x) or x == "none" else [a.strip() for a in str(x).split(",")]
    )

    rows = []

    for _, transformer in transformers.iterrows():
        user_ids = [u.strip() for u in str(transformer["connected_user_ids"]).split(",")]
        connected_users = users[users["user_id"].isin(user_ids)]
        max_pool_size = max(2, len(connected_users))

        for _, user in connected_users.iterrows():
            if not user["shiftable_list"]:
                continue

            for appliance in user["shiftable_list"]:
                base_kw = APPLIANCE_TYPICAL_KW.get(appliance, 1.5)

                for _ in range(SCENARIOS_PER_HOUSEHOLD_APPLIANCE):
                    appliance_kw = base_kw * np.random.uniform(0.7, 1.3)

                    simulated_loading_percent = np.clip(
                        transformer["loading_percent"] * np.random.uniform(0.5, 1.4),
                        10, 130
                    )
                    num_simultaneous = np.random.randint(1, max_pool_size + 1)

                    risk = compute_rebound_risk(
                        appliance_kw=appliance_kw,
                        rated_kva=transformer["rated_kva"],
                        loading_percent=simulated_loading_percent,
                        num_simultaneous=num_simultaneous,
                        flexibility_score=user["flexibility_score"],
                    )
                    risk += np.random.normal(0, 0.03)
                    risk = float(np.clip(risk, 0.0, 1.0))

                    label = bucket_risk(risk)

                    rows.append({
                        "user_id": user["user_id"],
                        "transformer_id": transformer["transformer_id"],
                        "appliance": appliance,
                        "appliance_kw": round(appliance_kw, 3),
                        "transformer_rated_kva": transformer["rated_kva"],
                        "transformer_loading_percent": round(simulated_loading_percent, 2),
                        "num_simultaneous_restarts": num_simultaneous,
                        "flexibility_score": user["flexibility_score"],
                        "carbon_priority_weight": user["carbon_priority_weight"],
                        "cost_priority_weight": user["cost_priority_weight"],
                        "rebound_risk_score": round(risk, 4),
                        "stagger_label": label,
                    })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_training_rows()
    os.makedirs("data/synthetic", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df)} training rows.")
    print(df["stagger_label"].value_counts())
    print(df.head())