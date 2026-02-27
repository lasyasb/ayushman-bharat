def calculate_hospital_risk(df):

    hospital_summary = df.groupby("hospital_id")["rule_score"].mean().reset_index()

    hospital_summary["hospital_risk"] = (
        hospital_summary["rule_score"].rank(pct=True) * 100
    )

    df = df.merge(
        hospital_summary[["hospital_id", "hospital_risk"]],
        on="hospital_id",
        how="left"
    )

    return df