import numpy as np
from config import RULE_WEIGHT, ML_WEIGHT, HOSPITAL_WEIGHT
from config import HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD

def calculate_final_risk(df):

    df["final_risk_score"] = (
        RULE_WEIGHT * df["rule_score"] +
        ML_WEIGHT * df["ml_score"] +
        HOSPITAL_WEIGHT * df["hospital_risk"]
    )

    conditions = [
        df["final_risk_score"] >= HIGH_RISK_THRESHOLD,
        df["final_risk_score"] >= MEDIUM_RISK_THRESHOLD
    ]

    choices = ["High", "Medium"]

    df["risk_level"] = np.select(conditions, choices, default="Low")

    return df