# api/app/services/baseline_predictor/train.py
import lightgbm as lgb
import numpy as np
import pandas as pd

def generate_synthetic_data(n=5000):
    np.random.seed(42)
    df = pd.DataFrame({
        "hour": np.random.randint(0, 24, n),
        "temp": np.random.normal(75, 10, n),
        "day_of_week": np.random.randint(0, 7, n),
    })
    df["kwh"] = 2 + 0.05 * df["temp"] + np.where(df["hour"].between(17, 20), 1.5, 0) + np.random.normal(0, 0.3, n)
    return df

def train_model():
    df = generate_synthetic_data()
    train_data = lgb.Dataset(df[["hour", "temp", "day_of_week"]], label=df["kwh"])
    model = lgb.train({"objective": "regression", "verbosity": -1}, train_data, num_boost_round=100)
    model.save_model("api/app/services/baseline_predictor/model.txt")
    return model

if __name__ == "__main__":
    train_model()
