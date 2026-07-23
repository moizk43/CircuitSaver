"""
load_weather_data.py
Pulls historical weather data from Open-Meteo for both Austin (Pecan Street)
and London (Smart Meters) date ranges and locations.
"""

import os
import requests
import pandas as pd

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

LOCATIONS = {
    "austin": {"latitude": 30.27, "longitude": -97.74},
    "london": {"latitude": 51.51, "longitude": -0.13},
}


def fetch_weather(location_name, start_date, end_date):
    coords = LOCATIONS[location_name]
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,cloud_cover",
        "timezone": "UTC",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["hourly"])
    df["location"] = location_name
    return df


if __name__ == "__main__":
    austin_weather = fetch_weather("austin", "2018-08-23", "2018-08-25")
    print("Austin weather shape:", austin_weather.shape)
    print(austin_weather.head())

    london_weather = fetch_weather("london", "2011-12-01", "2014-02-28")
    print("\nLondon weather shape:", london_weather.shape)
    print(london_weather.head())

    os.makedirs("data/raw", exist_ok=True)
    austin_weather.to_csv("data/raw/weather_austin.csv", index=False)
    london_weather.to_csv("data/raw/weather_london.csv", index=False)
    print("\nSaved both weather files to data/raw/")