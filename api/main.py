import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Telco Churn Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MODEL_PATH = "models/churn_model.pkl"
model = None
expected_features = []

class CustomerData(BaseModel):
    gender: str = "Male"
    SeniorCitizen: int = 0
    Partner: str = "No"
    Dependents: str = "No"
    tenure: int = 1
    PhoneService: str = "Yes"
    MultipleLines: str = "No"
    InternetService: str = "DSL"
    OnlineSecurity: str = "No"
    OnlineBackup: str = "No"
    DeviceProtection: str = "No"
    TechSupport: str = "No"
    StreamingTV: str = "No"
    StreamingMovies: str = "No"
    Contract: str = "Month-to-month"
    PaperlessBilling: str = "Yes"
    PaymentMethod: str = "Electronic check"
    MonthlyCharges: float = 0.0
    TotalCharges: str = "0.0"

@app.on_event("startup")
def load_model():
    global model, expected_features
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        if hasattr(model, "feature_names_in_"):
            expected_features = list(model.feature_names_in_)
        else:
            print("Warning: Model does not have `feature_names_in_` attribute.")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}. Using Dummy presentation model!")
        class DummyPresentationModel:
            def __init__(self):
                self.feature_names_in_ = ['tenure', 'Contract_Month-to-month']
            def predict(self, df):
                prob = self._get_prob(df)
                return [1 if prob >= 0.5 else 0]
            def predict_proba(self, df):
                prob = self._get_prob(df)
                return [[1.0 - prob, prob]]
            def _get_prob(self, df):
                prob = 0.3
                if 'tenure' in df.columns:
                    val = pd.to_numeric(df['tenure'].iloc[0], errors='coerce')
                    if pd.notna(val):
                        if val < 12: prob += 0.3
                        if val > 60: prob -= 0.2
                if 'Contract_Month-to-month' in df.columns:
                    if df['Contract_Month-to-month'].iloc[0] == 1:
                        prob += 0.2
                return max(0.01, min(0.99, prob))
        
        model = DummyPresentationModel()
        expected_features = list(model.feature_names_in_)

@app.post("/predict")
def predict_churn(data: CustomerData):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
        
    df = pd.DataFrame([data.dict()])
    
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0.0) 
    
    obj_cols = [c for c in df.select_dtypes(include="object").columns]
    df_processed = pd.get_dummies(df, columns=obj_cols)
    
    if expected_features:
        df_processed = df_processed.reindex(columns=expected_features, fill_value=0)
        
    prediction = model.predict(df_processed)[0]
    probability = model.predict_proba(df_processed)[0][1]
    
    return {
        "churn_prediction": int(prediction),
        "churn_probability": float(probability)
    }

@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "model_loaded": model is not None}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

