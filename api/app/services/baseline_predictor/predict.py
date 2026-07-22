# api/app/services/baseline_predictor/predict.py
import lightgbm as lgb

model = lgb.Booster(model_file="api/app/services/baseline_predictor/model.txt")

def predict_baseline(hour: int, temp: float, day_of_week: int):
    return model.predict([[hour, temp, day_of_week]])[0]
