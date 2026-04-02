import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.main import app
import api.main as main_module

client = TestClient(app)

class DummyModel:
    def __init__(self):
        self.feature_names_in_ = ["tenure", "MonthlyCharges", "SeniorCitizen", "gender_Male"]
    def predict(self, df):
        return [0]
    def predict_proba(self, df):
        return [[0.8, 0.2]]

@pytest.fixture(autouse=True)
def mock_model():
    original_model = main_module.model
    original_features = main_module.expected_features
    
    main_module.model = DummyModel()
    main_module.expected_features = list(DummyModel().feature_names_in_)
    
    yield
    
    main_module.model = original_model
    main_module.expected_features = original_features

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "model_loaded": True}

def test_predict():
    data = {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 50.0,
        "TotalCharges": "50.0"
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "churn_prediction" in result
    assert "churn_probability" in result
    assert result["churn_prediction"] == 0
    assert result["churn_probability"] == 0.2
