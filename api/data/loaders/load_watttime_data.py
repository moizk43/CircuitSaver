"""
load_watttime_data.py
Authenticates with WattTime and pulls recent grid carbon intensity data.
"""

import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from watttime import WattTimeMyAccess, WattTimeHistorical

load_dotenv()

WATTTIME_USERNAME = os.getenv("WATTTIME_USERNAME")
WATTTIME_PASSWORD = os.getenv("WATTTIME_PASSWORD")

REGION = "CAISO_NORTH"


def check_access():
    access = WattTimeMyAccess(username=WATTTIME_USERNAME, password=WATTTIME_PASSWORD)
    print(access.get_access_pandas())


def fetch_historical_carbon(start_date, end_date):
    historical = WattTimeHistorical(username=WATTTIME_USERNAME, password=WATTTIME_PASSWORD)
    df = historical.get_historical_pandas(
        start=start_date,
        end=end_date,
        region=REGION,
        signal_type="co2_moer",
    )
    return df


if __name__ == "__main__":
    check_access()

    end = datetime.now(timezone.utc) - timedelta(days=1)
    start = end - timedelta(days=3)

    carbon_df = fetch_historical_carbon(start_date=start, end_date=end)

    print("Carbon data shape:", carbon_df.shape)
    print(carbon_df.head())

    os.makedirs("data/raw", exist_ok=True)
    carbon_df.to_csv("data/raw/watttime_carbon.csv", index=False)
    print("Saved to data/raw/watttime_carbon.csv")