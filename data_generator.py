import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

hospitals = [f"HSP{i:03}" for i in range(1, 16)]
beneficiaries = [f"BEN{i:04}" for i in range(1, 301)]

procedures = {
    "PROC01": 25000,
    "PROC02": 120000,
    "PROC03": 180000,
    "PROC04": 40000,
    "PROC05": 75000
}

data = []

for i in range(500):
    claim_id = f"CLM{i:05}"
    beneficiary = random.choice(beneficiaries)
    hospital = random.choice(hospitals)
    procedure = random.choice(list(procedures.keys()))
    avg_cost = procedures[procedure]

    claim_amount = np.random.normal(avg_cost, avg_cost * 0.1)

    admission_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 180))
    stay_duration = random.randint(2, 7)
    discharge_date = admission_date + timedelta(days=stay_duration)

    data.append([
        claim_id,
        beneficiary,
        hospital,
        procedure,
        round(claim_amount, 2),
        admission_date,
        discharge_date,
        stay_duration
    ])

df = pd.DataFrame(data, columns=[
    "claim_id", "beneficiary_id", "hospital_id",
    "procedure_code", "claim_amount",
    "admission_date", "discharge_date", "stay_duration"
])

# Inject Fraud
fraud_indices = np.random.choice(df.index, size=50, replace=False)

for idx in fraud_indices:
    df.loc[idx, "claim_amount"] *= 2.5
    df.loc[idx, "stay_duration"] = 1

df.to_csv("claims.csv", index=False)

print("claims.csv generated successfully!")