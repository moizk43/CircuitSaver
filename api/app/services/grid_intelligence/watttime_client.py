# api/app/services/grid_intelligence/watttime_client.py
import httpx
import os

WATTTIME_USER = os.getenv("WATTTIME_USER")
WATTTIME_PASS = os.getenv("WATTTIME_PASS")

def get_watttime_token():
    resp = httpx.get("https://api.watttime.org/login", auth=(WATTTIME_USER, WATTTIME_PASS))
    return resp.json()["token"]

def fetch_carbon_signal(region="CAISO_NORTH"):
    token = get_watttime_token()
    return httpx.get("https://api.watttime.org/v3/signal-index",
                      headers={"Authorization": f"Bearer {token}"},
                      params={"region": region}).json()
