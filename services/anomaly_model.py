import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler

MODEL_PATH = "models/isolation_model.pkl"

def train_model(df):

    features = df[[
        "claim_amount",
        "stay_duration",
        "deviation",
        "patient_claim_count"
    ]]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(scaled)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump((model, scaler), f)

def run_inference(df):

    with open(MODEL_PATH, "rb") as f:
        model, scaler = pickle.load(f)

    features = df[[
        "claim_amount",
        "stay_duration",
        "deviation",
        "patient_claim_count"
    ]]

    scaled = scaler.transform(features)

    decision_scores = model.decision_function(scaled)

    inverted = (-decision_scores).reshape(-1, 1)

    scaler_mm = MinMaxScaler(feature_range=(0, 100))
    df["ml_score"] = scaler_mm.fit_transform(inverted)

    return df