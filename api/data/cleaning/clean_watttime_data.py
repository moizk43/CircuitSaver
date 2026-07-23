import pandas as pd

df = pd.read_csv("data/raw/watttime_carbon.csv")
df.loc[df["value"] <= 0, "value"] = pd.NA
df["value"] = df["value"].interpolate()
df.to_csv("data/raw/watttime_carbon_cleaned.csv", index=False)