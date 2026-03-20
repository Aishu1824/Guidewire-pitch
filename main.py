from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from sklearn.ensemble import IsolationForest

app = FastAPI()

# ---------------- ML MODEL TRAINING (Synthetic Data) ----------------

X_train = np.array([
    [0.85, 0, 0, 2],
    [0.78, 0, 0, 1],
    [0.92, 0, 0, 3],
    [0.15, 1, 1, 0],
    [0.20, 1, 0, 0],
    [0.10, 1, 1, 0],
])

model = IsolationForest(contamination=0.35, random_state=42)
model.fit(X_train)

def ml_fraud_prediction(movement_var, sudden_jump, ip_mismatch, orders):
    sample = np.array([[movement_var, sudden_jump, ip_mismatch, orders]])
    pred = model.predict(sample)
    return "FRAUD" if pred[0] == -1 else "SAFE"


# ---------------- RULE BASED LOGIC ----------------

def detect_disruption(rain, temp):
    return rain > 60 or temp > 40

def worker_valid(is_online, active_minutes):
    return is_online and active_minutes >= 30

def earnings_loss(orders):
    return orders == 0

def fraud_score(location_static, sudden_jump, orders, ip_mismatch):
    score = 0
    if location_static:
        score += 30
    if sudden_jump:
        score += 40
    if orders > 0:
        score += 50
    if ip_mismatch:
        score += 20
    return score

def payout_decision(disruption, valid_worker, loss, score):
    if disruption and valid_worker and loss and score < 30:
        return "FULL PAYOUT"
    elif 30 <= score <= 70:
        return "PARTIAL PAYOUT"
    else:
        return "BLOCKED"


# ---------------- INPUT MODEL ----------------

class ClaimInput(BaseModel):
    rain: float
    temperature: float
    is_online: int
    active_minutes: int
    orders_completed: int
    location_static: int
    sudden_jump: int
    ip_mismatch: int
    movement_variance: float


# ---------------- API ROUTE ----------------

@app.post("/claim")
def process_claim(data: ClaimInput):

    disruption = detect_disruption(data.rain, data.temperature)
    valid_worker = worker_valid(data.is_online, data.active_minutes)
    loss = earnings_loss(data.orders_completed)

    score = fraud_score(
        data.location_static,
        data.sudden_jump,
        data.orders_completed,
        data.ip_mismatch
    )

    ml_result = ml_fraud_prediction(
        data.movement_variance,
        data.sudden_jump,
        data.ip_mismatch,
        data.orders_completed
    )

    decision = payout_decision(disruption, valid_worker, loss, score)

    return {
        "disruption": disruption,
        "valid_worker": valid_worker,
        "income_loss": loss,
        "fraud_score": score,
        "ml_prediction": ml_result,
        "final_decision": decision
    }


@app.get("/")
def home():
    return {"message": "RISE Protocol API Running"}