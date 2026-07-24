"""
generate_user_profiles.py
Generates realistic synthetic household user profiles for CircuitSaver demo purposes.
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)

HOUSEHOLD_TYPES = ["family_of_4", "single_professional", "retired_couple", "student_apartment", "family_of_2_no_kids"]
REGIONS = ["Austin_TX", "London_UK"]

APPLIANCE_POOL = {
    "ev_charger": {"base_prob": 0.15, "kwh_range": (20, 60), "shiftable": True},
    "dishwasher": {"base_prob": 0.75, "kwh_range": (0.8, 1.8), "shiftable": True},
    "dryer": {"base_prob": 0.7, "kwh_range": (2.0, 4.0), "shiftable": True},
    "washing_machine": {"base_prob": 0.85, "kwh_range": (0.7, 1.5), "shiftable": True},
    "hvac": {"base_prob": 0.9, "kwh_range": (3.0, 8.0), "shiftable": False},
    "water_heater": {"base_prob": 0.65, "kwh_range": (1.5, 4.5), "shiftable": True},
    "pool_pump": {"base_prob": 0.08, "kwh_range": (1.0, 2.5), "shiftable": True},
}

HOUSEHOLD_PROFILE_BIAS = {
    "family_of_4": {"ev_charger": 0.30, "dryer": 0.85, "dishwasher": 0.90, "pool_pump": 0.15, "size_sqft": (1800, 3200), "occupants": 4},
    "single_professional": {"ev_charger": 0.25, "dryer": 0.55, "dishwasher": 0.60, "pool_pump": 0.03, "size_sqft": (600, 1200), "occupants": 1},
    "retired_couple": {"ev_charger": 0.08, "dryer": 0.65, "dishwasher": 0.70, "pool_pump": 0.10, "size_sqft": (1200, 2200), "occupants": 2},
    "student_apartment": {"ev_charger": 0.02, "dryer": 0.20, "dishwasher": 0.15, "pool_pump": 0.0, "size_sqft": (400, 800), "occupants": 3},
    "family_of_2_no_kids": {"ev_charger": 0.20, "dryer": 0.60, "dishwasher": 0.75, "pool_pump": 0.10, "size_sqft": (1000, 1800), "occupants": 2},
}

REGION_META = {
    "Austin_TX": {"timezone": "America/Chicago", "grid_region": "ERCOT"},
    "London_UK": {"timezone": "Europe/London", "grid_region": "GB"},
}

USAGE_WINDOWS = {
    "ev_charger": ("22:00", "06:00"),
    "dishwasher": ("19:00", "21:00"),
    "dryer": ("09:00", "11:00"),
    "washing_machine": ("08:00", "10:00"),
    "hvac": ("00:00", "23:59"),
    "water_heater": ("06:00", "08:00"),
    "pool_pump": ("10:00", "16:00"),
}

# Notification settings: what % of households are email-only (no smart device/app)
NOTIFICATION_METHODS = ["app", "email"]
NOTIFICATION_WEIGHTS = [0.70, 0.30]

# Manually override specific user_ids with real email addresses for live testing.
# Add your own real email here so you can actually receive a test message.
REAL_TEST_EMAILS = {
    "user_003": "moizkothawala@gmail.com",
    "user_007": "moizkothawala@gmail.com",
}


def sample_appliance_ownership(household_type):
    bias = HOUSEHOLD_PROFILE_BIAS[household_type]
    owned = {}
    for appliance, meta in APPLIANCE_POOL.items():
        prob = bias.get(appliance, meta["base_prob"])
        owned[appliance] = np.random.rand() < prob
    return owned


def sample_kwh(appliance):
    low, high = APPLIANCE_POOL[appliance]["kwh_range"]
    return round(np.random.uniform(low, high), 2)


def sample_flexibility(household_type):
    base = {
        "family_of_4": 0.45,
        "single_professional": 0.55,
        "retired_couple": 0.65,
        "student_apartment": 0.35,
        "family_of_2_no_kids": 0.50,
    }[household_type]
    return round(np.clip(np.random.normal(base, 0.15), 0.05, 0.98), 2)


def sample_priority_weights():
    carbon = np.random.beta(2, 2)
    cost = 1 - carbon + np.random.normal(0, 0.1)
    cost = float(np.clip(cost, 0.05, 0.95))
    carbon = float(np.clip(carbon, 0.05, 0.95))
    total = carbon + cost
    return round(carbon / total, 2), round(cost / total, 2)


def sample_notification_method():
    return np.random.choice(NOTIFICATION_METHODS, p=NOTIFICATION_WEIGHTS)


def generate_profile(user_id):
    household_type = np.random.choice(list(HOUSEHOLD_PROFILE_BIAS.keys()), p=[0.28, 0.24, 0.18, 0.15, 0.15])
    region = np.random.choice(REGIONS, p=[0.6, 0.4])
    bias = HOUSEHOLD_PROFILE_BIAS[household_type]
    region_meta = REGION_META[region]

    ownership = sample_appliance_ownership(household_type)
    owned_appliances = [a for a, has in ownership.items() if has]
    if not owned_appliances:
        owned_appliances = ["hvac"]

    appliance_kwh = {a: sample_kwh(a) for a in owned_appliances}
    shiftable_appliances = [a for a in owned_appliances if APPLIANCE_POOL[a]["shiftable"]]

    sqft_low, sqft_high = bias["size_sqft"]
    home_sqft = int(np.random.uniform(sqft_low, sqft_high))

    flexibility = sample_flexibility(household_type)
    carbon_weight, cost_weight = sample_priority_weights()

    avg_monthly_kwh = round(sum(appliance_kwh.values()) * np.random.uniform(20, 30) + home_sqft * 0.04, 1)

    notification_method = sample_notification_method()
    if user_id in REAL_TEST_EMAILS:
        notification_method = "email"
        email_address = REAL_TEST_EMAILS[user_id]
    else:
        email_address = f"{user_id.lower()}@example.com"

    return {
        "user_id": user_id,
        "household_type": household_type,
        "occupants": bias["occupants"] + np.random.choice([-1, 0, 0, 1]),
        "region": region,
        "grid_region": region_meta["grid_region"],
        "timezone": region_meta["timezone"],
        "home_sqft": home_sqft,
        "appliances_owned": ",".join(owned_appliances),
        "shiftable_appliances": ",".join(shiftable_appliances) if shiftable_appliances else "none",
        "appliance_avg_kwh_per_use": ";".join(f"{a}:{v}" for a, v in appliance_kwh.items()),
        "typical_usage_windows": ";".join(f"{a}:{USAGE_WINDOWS[a][0]}-{USAGE_WINDOWS[a][1]}" for a in owned_appliances),
        "flexibility_score": flexibility,
        "carbon_priority_weight": carbon_weight,
        "cost_priority_weight": cost_weight,
        "avg_monthly_kwh": avg_monthly_kwh,
        "notification_method": notification_method,
        "email_address": email_address,
    }


def generate_all_profiles(n=50):
    return pd.DataFrame([generate_profile(f"user_{i:03d}") for i in range(n)])


if __name__ == "__main__":
    df = generate_all_profiles(n=50)
    os.makedirs("data/synthetic", exist_ok=True)
    df.to_csv("data/synthetic/user_profiles.csv", index=False)
    print(f"Generated {len(df)} synthetic user profiles.")
    print(f"Email-notify households: {(df['notification_method'] == 'email').sum()} / {len(df)}")
    print(df.head())