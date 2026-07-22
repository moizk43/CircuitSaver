# api/app/services/grid_intelligence/cron.py
from apscheduler.schedulers.background import BackgroundScheduler
from .watttime_client import fetch_carbon_signal
from .open_meteo_client import fetch_weather

def fetch_grid_data():
    carbon = fetch_carbon_signal()
    weather = fetch_weather()
    # write carbon + weather into GridSignal table here

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_grid_data, "interval", minutes=5)
scheduler.start()
