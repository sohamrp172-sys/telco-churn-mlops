import io
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.preprocess import preprocess


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def raw_csv(tmp_path):
    """Minimal raw telco CSV matching the real schema."""
    data = {
        "customerID": ["0001-A", "0002-B", "0003-C"],
        "gender": ["Male", "Female", "Male"],
        "SeniorCitizen": [0, 1, 0],
        "Partner": ["Yes", "No", "Yes"],
        "Dependents": ["No", "No", "Yes"],
        "tenure": [12, 24, 6],
        "PhoneService": ["Yes", "No", "Yes"],
        "MultipleLines": ["No", "No phone service", "Yes"],
        "InternetService": ["DSL", "Fiber optic", "No"],
        "OnlineSecurity": ["No", "Yes", "No internet service"],
        "OnlineBackup": ["Yes", "No", "No internet service"],
        "DeviceProtection": ["No", "Yes", "No internet service"],
        "TechSupport": ["No", "No", "No internet service"],
        "StreamingTV": ["No", "Yes", "No internet service"],
        "StreamingMovies": ["No", "Yes", "No internet service"],
        "Contract": ["Month-to-month", "One year", "Two year"],
        "PaperlessBilling": ["Yes", "No", "Yes"],
        "PaymentMethod": ["Electronic check", "Mailed check", "Bank transfer (automatic)"],
        "MonthlyCharges": [29.85, 56.95, 20.0],
        "TotalCharges": ["358.20", " ", "120.0"],  # blank simulates real data NaN
        "Churn": ["No", "Yes", "No"],
    }
    path = tmp_path / "raw.csv"
    pd.DataFrame(data).to_csv(path, index=False)
    return path


@pytest.fixture
def processed_csv(raw_csv, tmp_path):
    out = tmp_path / "processed.csv"
    preprocess(str(raw_csv), str(out))
    return out


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPreprocess:

    def test_output_file_created(self, processed_csv):
        assert processed_csv.exists()

    def test_customer_id_dropped(self, processed_csv):
        df = pd.read_csv(processed_csv)
        assert "customerID" not in df.columns

    def test_churn_is_binary_int(self, processed_csv):
        df = pd.read_csv(processed_csv)
        assert set(df["Churn"].unique()).issubset({0, 1})
        assert df["Churn"].dtype in [int, "int64", "int32"]

    def test_total_charges_numeric_no_nan(self, processed_csv):
        df = pd.read_csv(processed_csv)
        assert pd.api.types.is_numeric_dtype(df["TotalCharges"])
        assert df["TotalCharges"].isna().sum() == 0

    def test_no_object_columns_remain(self, processed_csv):
        df = pd.read_csv(processed_csv)
        obj_cols = df.select_dtypes(include="object").columns.tolist()
        assert obj_cols == [], f"Unexpected object columns: {obj_cols}"

    def test_row_count_preserved(self, raw_csv, processed_csv):
        raw = pd.read_csv(raw_csv)
        processed = pd.read_csv(processed_csv)
        assert len(raw) == len(processed)

    def test_column_count_expands(self, raw_csv, processed_csv):
        raw = pd.read_csv(raw_csv)
        processed = pd.read_csv(processed_csv)
        assert processed.shape[1] > raw.shape[1]

    def test_churn_no_maps_to_zero(self, raw_csv, processed_csv):
        raw = pd.read_csv(raw_csv)
        processed = pd.read_csv(processed_csv)
        no_churn_idx = raw[raw["Churn"] == "No"].index
        assert (processed.loc[no_churn_idx, "Churn"] == 0).all()

    def test_churn_yes_maps_to_one(self, raw_csv, processed_csv):
        raw = pd.read_csv(raw_csv)
        processed = pd.read_csv(processed_csv)
        yes_churn_idx = raw[raw["Churn"] == "Yes"].index
        assert (processed.loc[yes_churn_idx, "Churn"] == 1).all()
