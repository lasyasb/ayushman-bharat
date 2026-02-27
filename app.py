from flask import Flask, render_template, request, redirect
import pandas as pd
from database.db import get_connection
from services.feature_engineering import create_features
from services.rule_engine import apply_rules
from services.anomaly_model import run_inference
from services.hospital_risk import calculate_hospital_risk
from services.risk_engine import calculate_final_risk
app = Flask(__name__)


@app.route("/")
def dashboard():

    from database.db import get_connection
    conn = get_connection()

    df = pd.read_sql_query("SELECT * FROM claims", conn)
    conn.close()

    filtered = df.copy()

    risk = request.args.get("risk")
    search = request.args.get("claim_id")

    if risk and risk != "All":
        filtered = filtered[filtered["risk_level"] == risk]

    if search:
        filtered = filtered[
            filtered["claim_id"].str.contains(search, case=False)
        ]

    monthly = df.groupby("month").agg(
        total=("claim_id", "count"),
        high=("risk_level", lambda x: (x == "High").sum())
    ).reset_index()

    monthly["fraud_rate"] = (
        monthly["high"] / monthly["total"]
    ) * 100

    return render_template(
        "dashboard.html",
        claims=filtered.to_dict(orient="records"),
        monthly=monthly.to_dict(orient="records"),
        total=len(df),
        high=len(df[df["risk_level"] == "High"]),
        medium=len(df[df["risk_level"] == "Medium"]),
        low=len(df[df["risk_level"] == "Low"])
    )

@app.route("/claim/<claim_id>")
def claim_view(claim_id):

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM claims", conn)
    conn.close()

    claim = df[df["claim_id"] == claim_id].iloc[0]

    beneficiary_claims = df[
        df["beneficiary_id"] == claim["beneficiary_id"]
    ].sort_values("admission_date")

    return render_template(
        "claim.html",
        claim=claim,
        history=beneficiary_claims.to_dict(orient="records")
    )

@app.route("/hospital/<hospital_id>")
def hospital_view(hospital_id):
    conn = get_connection()

    hospital_claims = pd.read_sql_query("""
        SELECT * FROM claims
        WHERE hospital_id = ?
        ORDER BY admission_date
    """, conn, params=(hospital_id,))

    conn.close()

    return render_template(
        "hospital.html",
        hospital_id=hospital_id,
        claims=hospital_claims.to_dict(orient="records")
    )

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("upload.html", message="No file selected.")

        try:
            new_df = pd.read_csv(file)
        except Exception:
            return render_template("upload.html", message="Invalid CSV file.")

        required_columns = [
            "claim_id",
            "beneficiary_id",
            "hospital_id",
            "procedure_code",
            "claim_amount",
            "admission_date",
            "discharge_date",
            "stay_duration"
        ]

        for col in required_columns:
            if col not in new_df.columns:
                return render_template(
                    "upload.html",
                    message=f"Missing required column: {col}"
                )

        conn = get_connection()
        existing_df = pd.read_sql_query("SELECT claim_id FROM claims", conn)

        total_uploaded = len(new_df)

        new_df = new_df[
            ~new_df["claim_id"].isin(existing_df["claim_id"])
        ]

        duplicates = total_uploaded - len(new_df)

        if len(new_df) == 0:
            conn.close()
            return render_template(
                "upload.html",
                message=f"All {duplicates} records were duplicates. Nothing inserted."
            )

        # Run fraud pipeline
        new_df = create_features(new_df)
        new_df = apply_rules(new_df)
        new_df = run_inference(new_df)
        new_df = calculate_hospital_risk(new_df)
        new_df = calculate_final_risk(new_df)

        # Insert
        new_df.to_sql("claims", conn, if_exists="append", index=False)
        conn.close()

        inserted = len(new_df)

        if len(new_df) > 300:
            preview = new_df.head(300).to_dict(orient="records")
        else:
            preview = new_df.to_dict(orient="records")

        return render_template(
            "upload.html",
            message=f"Upload Successful",
            total=total_uploaded,
            inserted=inserted,
            duplicates=duplicates,
            preview=preview
        )

    return render_template("upload.html")

@app.route("/months")
def month_view():
    conn = get_connection()

    monthly = pd.read_sql_query("""
        SELECT 
            month,
            COUNT(*) as total_claims,
            AVG(claim_amount) as avg_amount,
            SUM(CASE WHEN risk_level='High' THEN 1 ELSE 0 END) as high_risk
        FROM claims
        GROUP BY month
        ORDER BY month
    """, conn)

    conn.close()

    return render_template(
        "months.html",
        monthly=monthly.to_dict(orient="records")
    )
@app.route("/patient/<patient_id>")
def patient_view(patient_id):
    conn = get_connection()

    patient_claims = pd.read_sql_query("""
        SELECT * FROM claims
        WHERE beneficiary_id = ?
        ORDER BY admission_date
    """, conn, params=(patient_id,))

    conn.close()

    return render_template(
        "patient.html",
        patient_id=patient_id,
        claims=patient_claims.to_dict(orient="records")
    )
@app.route("/database")
def database_view():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM claims", conn)
    conn.close()

    return render_template(
        "database.html",
        data=df.to_dict(orient="records"),
        columns=df.columns
    )

if __name__ == "__main__":
    app.run(debug=True)