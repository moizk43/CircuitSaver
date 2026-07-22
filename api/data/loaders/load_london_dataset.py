"""
load_london_dataset.py
Loads the London Smart Meters daily consumption dataset via kagglehub.
"""

import os
import kagglehub
from kagglehub import KaggleDatasetAdapter

# Ensure Kaggle credentials are available (kaggle.json in ~/.kaggle/)
# Alternatively, uncomment and set these directly:
# os.environ['KAGGLE_USERNAME'] = "your_username"
# os.environ['KAGGLE_KEY'] = "your_key"


def load_london_daily_data():
    """Loads the daily aggregated London Smart Meters dataset as a DataFrame."""
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "jeanmidev/smart-meters-in-london",
        "daily_dataset.csv",
    )
    return df


def load_household_metadata():
    """Loads household metadata (tariff type, ACORN group) for joining later."""
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "jeanmidev/smart-meters-in-london",
        "informations_households.csv",
    )
    return df


if __name__ == "__main__":
    consumption_df = load_london_daily_data()
    households_df = load_household_metadata()

    print("Consumption data shape:", consumption_df.shape)
    print(consumption_df.head())

    print("\nHousehold metadata shape:", households_df.shape)
    print(households_df.head())

    # Save locally as CSV so you don't have to re-download every time
    os.makedirs("api/data/raw", exist_ok=True)
    consumption_df.to_csv("api/data/raw/london_daily_consumption.csv", index=False)
    households_df.to_csv("api/data/raw/london_households.csv", index=False)
    print("\nSaved to api/data/raw/")