"""
swarm_engine.py
Capacity Allocator: given a peak event requiring a load shed target on a
specific transformer, allocates how much each connected household should
shed, prioritizing carbon/cost savings first, then flexibility, while
distributing the burden fairly via a weighted water-filling algorithm.
"""

import ast
import pandas as pd

USER_PROFILES_PATH = "data/synthetic/user_profiles.csv"
TRANSFORMER_TOPOLOGY_PATH = "data/synthetic/transformer_topology.csv"

CARBON_WEIGHT = 0.4
COST_WEIGHT = 0.4
FLEXIBILITY_WEIGHT = 0.2

DEFAULT_PEAK_RATE_USD_PER_KWH = 0.15
DEFAULT_CO2_LBS_PER_KWH = 0.85

_cached_users = None
_cached_transformers = None


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


def load_users():
    global _cached_users
    if _cached_users is not None:
        return _cached_users

    df = pd.read_csv(USER_PROFILES_PATH)
    df["appliance_kwh_map"] = df["appliance_avg_kwh_per_use"].apply(parse_appliance_kwh)
    df["shiftable_list"] = df["shiftable_appliances"].apply(
        lambda x: [] if pd.isna(x) or x == "none" else [a.strip() for a in str(x).split(",")]
    )

    def compute_capacity(row):
        return sum(
            row["appliance_kwh_map"].get(app, 0.0)
            for app in row["shiftable_list"]
        )

    df["shiftable_capacity_kwh"] = df.apply(compute_capacity, axis=1)

    def priority_score(row):
        return (
            CARBON_WEIGHT * row["carbon_priority_weight"]
            + COST_WEIGHT * row["cost_priority_weight"]
            + FLEXIBILITY_WEIGHT * row["flexibility_score"]
        )

    df["priority_score"] = df.apply(priority_score, axis=1)

    _cached_users = df
    return df


def load_transformers():
    global _cached_transformers
    if _cached_transformers is not None:
        return _cached_transformers

    df = pd.read_csv(TRANSFORMER_TOPOLOGY_PATH)
    _cached_transformers = df
    return df


def get_transformer_households(transformer_id):
    transformers = load_transformers()
    row = transformers[transformers["transformer_id"] == transformer_id]
    if row.empty:
        raise ValueError(f"Transformer '{transformer_id}' not found in topology.")

    user_ids = [u.strip() for u in str(row.iloc[0]["connected_user_ids"]).split(",")]
    users = load_users()
    connected = users[users["user_id"].isin(user_ids)].copy()

    if connected.empty:
        raise ValueError(f"No matching users found for transformer '{transformer_id}'.")

    return connected, row.iloc[0]


def water_fill_allocate(households_df, shed_target_kw, max_iterations=50):
    households = households_df.copy().reset_index(drop=True)
    households["allocated_kw"] = 0.0
    households["is_capped"] = False

    remaining_target = shed_target_kw

    for _ in range(max_iterations):
        active = households[~households["is_capped"]]
        if active.empty or remaining_target <= 1e-6:
            break

        score_sum = active["priority_score"].sum()
        if score_sum <= 0:
            weights = pd.Series(1.0 / len(active), index=active.index)
        else:
            weights = active["priority_score"] / score_sum

        proposed_allocation = weights * remaining_target

        any_capped_this_round = False
        for idx in active.index:
            proposed = proposed_allocation.loc[idx]
            capacity_left = households.loc[idx, "shiftable_capacity_kwh"] - households.loc[idx, "allocated_kw"]

            if proposed >= capacity_left:
                households.loc[idx, "allocated_kw"] += capacity_left
                households.loc[idx, "is_capped"] = True
                remaining_target -= capacity_left
                any_capped_this_round = True
            else:
                households.loc[idx, "allocated_kw"] += proposed
                remaining_target -= proposed

        if not any_capped_this_round:
            break

    total_allocated = households["allocated_kw"].sum()
    shortfall_kw = max(0.0, shed_target_kw - total_allocated)

    return households, shortfall_kw


def recommend_appliance(row):
    if not row["appliance_kwh_map"] or not row["shiftable_list"]:
        return None

    shiftable_with_kwh = {
        app: row["appliance_kwh_map"].get(app, 0.0)
        for app in row["shiftable_list"]
    }
    if not shiftable_with_kwh:
        return None

    return max(shiftable_with_kwh, key=shiftable_with_kwh.get)


def allocate_capacity(
    transformer_id,
    shed_target_kw,
    current_co2_lbs_per_kwh=DEFAULT_CO2_LBS_PER_KWH,
    peak_rate_usd_per_kwh=DEFAULT_PEAK_RATE_USD_PER_KWH,
):
    households, transformer_row = get_transformer_households(transformer_id)

    allocated_df, shortfall_kw = water_fill_allocate(households, shed_target_kw)

    allocated_df["recommended_appliance"] = allocated_df.apply(recommend_appliance, axis=1)
    allocated_df["estimated_carbon_saved_lbs"] = allocated_df["allocated_kw"] * current_co2_lbs_per_kwh
    allocated_df["estimated_cost_saved_usd"] = allocated_df["allocated_kw"] * peak_rate_usd_per_kwh

    result_columns = [
        "user_id", "household_type", "region", "allocated_kw",
        "shiftable_capacity_kwh", "priority_score", "recommended_appliance",
        "estimated_carbon_saved_lbs", "estimated_cost_saved_usd", "is_capped",
    ]
    result = allocated_df[result_columns].sort_values("allocated_kw", ascending=False).reset_index(drop=True)

    summary = {
        "transformer_id": transformer_id,
        "shed_target_kw": shed_target_kw,
        "total_allocated_kw": round(allocated_df["allocated_kw"].sum(), 3),
        "shortfall_kw": round(shortfall_kw, 3),
        "households_involved": len(allocated_df),
        "total_carbon_saved_lbs": round(result["estimated_carbon_saved_lbs"].sum(), 3),
        "total_cost_saved_usd": round(result["estimated_cost_saved_usd"].sum(), 3),
        "transformer_rated_kva": transformer_row["rated_kva"],
        "transformer_status_before": transformer_row["status"],
    }

    return summary, result


if __name__ == "__main__":
    transformers = load_transformers()
    example_transformer_id = transformers.iloc[0]["transformer_id"]

    summary, result = allocate_capacity(
        transformer_id=example_transformer_id,
        shed_target_kw=5.0,
    )

    print("=== Allocation Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    print("\n=== Per-Household Allocation ===")
    print(result.to_string(index=False))