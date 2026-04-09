import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

app = FastAPI(title="Telco Churn Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Get absolute path to model file
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"
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
    print(f"Attempting to load model from: {MODEL_PATH}")
    print(f"Model path absolute: {MODEL_PATH.absolute()}")
    print(f"Model path exists: {MODEL_PATH.exists()}")
    print(f"Current working directory: {os.getcwd()}")
    
    if MODEL_PATH.exists():
        print(f"✓ Model file found at {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
        if hasattr(model, "feature_names_in_"):
            expected_features = list(model.feature_names_in_)
            print(f"✓ Model loaded successfully with {len(expected_features)} features")
            print(f"✓ Using REAL trained model (not dummy)")
        else:
            print("Warning: Model does not have `feature_names_in_` attribute.")
    else:
        print(f"✗ Model not found at {MODEL_PATH}. Using Dummy presentation model!")
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
    
    # Apply same feature engineering as in preprocessing
    df["ChargesPerTenure"] = df["MonthlyCharges"] / (df["tenure"] + 1)
    
    add_on_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]
    df["HasAddOns"] = df[add_on_cols].apply(
        lambda row: int(any(v == "Yes" for v in row)), axis=1
    )
    
    df["IsLongTermContract"] = df["Contract"].apply(
        lambda x: 1 if x in ["One year", "Two year"] else 0
    )
    
    df["AutoPay"] = df["PaymentMethod"].apply(
        lambda x: 1 if x in ["Bank transfer (automatic)", "Credit card (automatic)"] else 0
    )
    
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
    model_type = "real_trained_model" if model and not isinstance(model, type(model).__name__) == "DummyPresentationModel" else "dummy_model"
    model_info = {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_type": type(model).__name__ if model else None,
        "is_dummy": "Dummy" in type(model).__name__ if model else False,
        "feature_count": len(expected_features) if expected_features else 0,
        "model_path": str(MODEL_PATH),
        "model_exists": MODEL_PATH.exists()
    }
    return model_info

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

