import pandas as pd

from services.feature_engineering import create_features
from services.rule_engine import apply_rules
from services.anomaly_model import train_model, run_inference
from services.hospital_risk import calculate_hospital_risk
from services.risk_engine import calculate_final_risk
from database.db import get_connection

df = pd.read_csv("claims.csv")

df = create_features(df)
df = apply_rules(df)

train_model(df)
df = run_inference(df)

df = calculate_hospital_risk(df)
df = calculate_final_risk(df)

df.to_csv("final_claims.csv", index=False)

print("Advanced fraud pipeline completed.")

conn = get_connection()
df.to_sql("claims", conn, if_exists="replace", index=False)
conn.close()

print("Saved to SQLite database fraud.db")