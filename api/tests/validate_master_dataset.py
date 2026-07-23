import pandas as pd

df = pd.read_csv("data/processed/master_dataset.csv")

print(df["region"].value_counts())
print(df["household_id"].nunique())
print(df["user_id"].nunique())
print(df["transformer_id"].nunique())
print(df[["timestamp", "load_kw"]].describe())