import pandas as pd

def create_features(df):

    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["month"] = df["admission_date"].dt.to_period("M").astype(str)

    procedure_avg = df.groupby("procedure_code")["claim_amount"].transform("mean")
    df["deviation"] = df["claim_amount"] / procedure_avg

    patient_freq = df.groupby("beneficiary_id")["claim_id"].transform("count")
    df["patient_claim_count"] = patient_freq

    hospital_avg = df.groupby("hospital_id")["claim_amount"].transform("mean")
    df["hospital_avg_claim"] = hospital_avg

    return df