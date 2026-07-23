"""
inspect_pecan_street.py
Loads and inspects the manually downloaded Pecan Street dataset.
"""

import pandas as pd

FILE_PATH = "data/raw/PecanStreet_10_Homes_1Min_Data.csv"


def load_csv_safely(filepath):
    encodings_to_try = ["utf-8", "utf-16", "latin-1", "cp1252"]
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(filepath, encoding=enc, low_memory=False)
            print(f"Loaded successfully with encoding: {enc}")
            return df
        except Exception as e:
            print(f"Failed with {enc}: {type(e).__name__}")
    raise ValueError(f"Could not read {filepath} with any known encoding.")


if __name__ == "__main__":
    df = load_csv_safely(FILE_PATH)

    print("\nShape:", df.shape)
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nData types:")
    print(df.dtypes)
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nMissing values per column:")
    print(df.isnull().sum())


print("\nUnique Circuit values:")
print(df["Circuit"].unique())

print("\nUnique Measure values:")
print(df["Measure"].unique())

print("\nUnique Home IDs:")
print(df["Home ID"].unique())