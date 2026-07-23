"""
process_pecan_street.py
Filters to Real Power only, pivots long-format data into wide format,
and saves a clean training-ready CSV.
"""

import os
import pandas as pd

RAW_PATH = "data/raw/PecanStreet_10_Homes_1Min_Data.csv"
OUTPUT_PATH = "data/raw/pecan_street_wide.csv"


def load_and_filter():
    df = pd.read_csv(RAW_PATH, encoding="utf-8", low_memory=False)
    df["Datetime (UTC)"] = pd.to_datetime(df["Datetime (UTC)"])

    real_power_df = df[df["Measure"] == "Real Power"].copy()
    print("Filtered to Real Power only. Shape:", real_power_df.shape)
    return real_power_df


def pivot_to_wide(df):
    wide_df = df.pivot_table(
        index=["Home ID", "Datetime (UTC)"],
        columns="Circuit",
        values="Value"
    ).reset_index()

    wide_df.columns.name = None
    wide_df = wide_df.rename(columns={
        "HVAC Condenser": "hvac_condenser_kw",
        "HVAC Fan": "hvac_fan_kw",
        "Solar": "solar_generation_kw",
        "Main Panel": "total_home_power_kw",
        "Home ID": "home_id",
        "Datetime (UTC)": "timestamp",
    })

    return wide_df


if __name__ == "__main__":
    filtered = load_and_filter()
    wide = pivot_to_wide(filtered)

    print("\nWide format shape:", wide.shape)
    print(wide.head())
    print("\nMissing values per column:")
    print(wide.isnull().sum())

    os.makedirs("data/raw", exist_ok=True)
    wide.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved wide-format data to {OUTPUT_PATH}")