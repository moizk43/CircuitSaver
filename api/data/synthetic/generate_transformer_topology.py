"""
generate_transformer_topology.py
Generates a synthetic distribution transformer topology dataset,
clustering existing synthetic user profiles under realistic transformers.
"""

import os
import numpy as np
import pandas as pd

np.random.seed(7)

STANDARD_KVA_RATINGS = [15, 25, 37.5, 50, 75, 100, 150, 225, 300]

REGION_GRID_SPECS = {
    "Austin_TX": {"grid_region": "ERCOT", "primary_kv": 12.47, "secondary_v": 240, "phase_config": "1-phase", "mounting_options": ["pole_mounted", "pad_mounted"]},
    "London_UK": {"grid_region": "GB", "primary_kv": 11.0, "secondary_v": 400, "phase_config": "3-phase", "mounting_options": ["pad_mounted", "underground_vault"]},
}

DIVERSITY_FACTOR_RANGE = (0.55, 0.75)
HOUSEHOLDS_PER_TRANSFORMER_RANGE = (3, 9)


def pick_standard_kva(required_kva):
    for rating in STANDARD_KVA_RATINGS:
        if rating >= required_kva:
            return rating
    return STANDARD_KVA_RATINGS[-1]


def build_transformers(users_df):
    transformers = []
    transformer_counter = 0

    for region, region_users in users_df.groupby("region"):
        region_users = region_users.sample(frac=1, random_state=7).reset_index(drop=True)
        spec = REGION_GRID_SPECS[region]

        idx = 0
        while idx < len(region_users):
            cluster_size = np.random.randint(*HOUSEHOLDS_PER_TRANSFORMER_RANGE)
            cluster = region_users.iloc[idx: idx + cluster_size]
            idx += cluster_size
            if len(cluster) == 0:
                continue

            transformer_counter += 1
            transformer_id = f"XFMR_{region[:3].upper()}_{transformer_counter:03d}"

            connected_kw = cluster["avg_monthly_kwh"].sum() / (30 * 24)
            diversity_factor = round(np.random.uniform(*DIVERSITY_FACTOR_RANGE), 2)
            coincident_peak_kw = round(connected_kw * diversity_factor * np.random.uniform(3.5, 5.5), 2)

            power_factor = round(np.random.uniform(0.92, 0.98), 2)
            required_kva = coincident_peak_kw / power_factor
            rated_kva = pick_standard_kva(required_kva)

            loading_percent = round((required_kva / rated_kva) * 100, 1)

            install_year = int(np.random.choice(range(1998, 2024)))
            age_years = 2026 - install_year

            base_failure_risk = 0.02 + (age_years / 100) + max(0, (loading_percent - 80) / 200)
            failure_risk_score = round(np.clip(base_failure_risk + np.random.normal(0, 0.01), 0.01, 0.95), 3)

            mounting_type = np.random.choice(spec["mounting_options"])

            transformers.append({
                "transformer_id": transformer_id,
                "region": region,
                "grid_region": spec["grid_region"],
                "primary_voltage_kv": spec["primary_kv"],
                "secondary_voltage_v": spec["secondary_v"],
                "phase_config": spec["phase_config"],
                "mounting_type": mounting_type,
                "rated_kva": rated_kva,
                "connected_household_count": len(cluster),
                "connected_user_ids": ",".join(cluster["user_id"].tolist()),
                "avg_connected_load_kw": round(connected_kw, 2),
                "diversity_factor": diversity_factor,
                "coincident_peak_kw": coincident_peak_kw,
                "power_factor": power_factor,
                "loading_percent": loading_percent,
                "install_year": install_year,
                "age_years": age_years,
                "failure_risk_score": failure_risk_score,
                "status": "overloaded" if loading_percent > 100 else ("high_load" if loading_percent > 80 else "normal"),
            })

    return pd.DataFrame(transformers)


if __name__ == "__main__":
    users_df = pd.read_csv("data/synthetic/user_profiles.csv")
    transformers_df = build_transformers(users_df)
    os.makedirs("data/synthetic", exist_ok=True)
    transformers_df.to_csv("data/synthetic/transformer_topology.csv", index=False)
    print(f"Generated {len(transformers_df)} synthetic transformers.")
    print(transformers_df.head())
    