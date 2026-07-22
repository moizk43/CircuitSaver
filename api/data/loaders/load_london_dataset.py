"""
load_london_dataset.py
Downloads the London Smart Meters dataset, then loads it manually with pandas.
"""

import os
import glob
import pandas as pd
import kagglehub

def download_london_dataset():
    """Downloads the full dataset folder to local cache and returns the path."""
    path = kagglehub.dataset_download("jeanmidev/smart-meters-in-london")
    print("Dataset downloaded to:", path)
    return path


def find_file(path, filename):
    matches = glob.glob(os.path.join(path, "**", filename), recursive=True)
    if not matches:
        raise FileNotFoundError(f"{filename} not found in {path}")
    return matches[0]


def load_csv_safely(filepath):
    """Tries multiple encodings until one works, printing which one succeeded."""
    encodings_to_try = ["utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1", "cp1252"]
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            print(f"Successfully loaded with encoding: {enc}")
            return df
        except Exception as e:
            print(f"Failed with {enc}: {type(e).__name__}")
    raise ValueError(f"Could not read {filepath} with any known encoding.")


if __name__ == "__main__":
    dataset_path = download_london_dataset()

    daily_csv_path = find_file(dataset_path, "daily_dataset.csv")
    households_csv_path = find_file(dataset_path, "informations_households.csv")

    consumption_df = load_csv_safely(daily_csv_path)
    households_df = load_csv_safely(households_csv_path)

    print("Consumption data shape:", consumption_df.shape)
    print(consumption_df.head())

    print("\nHousehold metadata shape:", households_df.shape)
    print(households_df.head())

    os.makedirs("data/raw", exist_ok=True)
    consumption_df.to_csv("data/raw/london_daily_consumption.csv", index=False)
    households_df.to_csv("data/raw/london_households.csv", index=False)
    print("\nSaved to data/raw/")