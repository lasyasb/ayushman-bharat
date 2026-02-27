from config import TOTAL_RULES

def apply_rules(df):

    df["rules_triggered"] = 0
    df["fraud_reasons"] = ""

    # Rule 1: High deviation
    cond1 = df["deviation"] > 2
    df.loc[cond1, "rules_triggered"] += 1
    df.loc[cond1, "fraud_reasons"] += "High Cost Deviation; "

    # Rule 2: Abnormal stay
    cond2 = df["stay_duration"] <= 1
    df.loc[cond2, "rules_triggered"] += 1
    df.loc[cond2, "fraud_reasons"] += "Abnormal Stay; "

    # Rule 3: Duplicate claim
    duplicates = df.duplicated(
        subset=["beneficiary_id", "procedure_code", "admission_date"],
        keep=False
    )
    df.loc[duplicates, "rules_triggered"] += 1
    df.loc[duplicates, "fraud_reasons"] += "Duplicate Claim; "

    # Rule 4: Frequent patient
    cond4 = df["patient_claim_count"] > 5
    df.loc[cond4, "rules_triggered"] += 1
    df.loc[cond4, "fraud_reasons"] += "High Patient Frequency; "

    # Rule 5: Hospital inflation
    cond5 = df["claim_amount"] > df["hospital_avg_claim"] * 1.8
    df.loc[cond5, "rules_triggered"] += 1
    df.loc[cond5, "fraud_reasons"] += "Hospital Inflation Pattern; "

    df["rule_score"] = (df["rules_triggered"] / TOTAL_RULES) * 100

    return df