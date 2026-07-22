# api/app/services/grid_intelligence/open_meteo_client.py
import httpx

def fetch_weather(lat=41.68, lon=-86.25):
    return httpx.get("https://api.open-meteo.com/v1/forecast",
                      params={"latitude": lat, "longitude": lon,
                              "current": "temperature_2m"}).json()
