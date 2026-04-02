import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

data = {
    'gender': ['Male', 'Female', 'Male'],
    'SeniorCitizen': [0, 1, 0],
    'Partner': ['Yes', 'No', 'Yes'],
    'Dependents': ['No', 'Yes', 'No'],
    'tenure': [1, 24, 72],
    'PhoneService': ['Yes', 'Yes', 'Yes'],
    'MultipleLines': ['No', 'Yes', 'No'],
    'InternetService': ['DSL', 'Fiber optic', 'No'],
    'OnlineSecurity': ['No', 'Yes', 'No internet service'],
    'OnlineBackup': ['No', 'No', 'No internet service'],
    'DeviceProtection': ['No', 'No', 'No internet service'],
    'TechSupport': ['No', 'Yes', 'No internet service'],
    'StreamingTV': ['No', 'Yes', 'No internet service'],
    'StreamingMovies': ['No', 'Yes', 'No internet service'],
    'Contract': ['Month-to-month', 'One year', 'Two year'],
    'PaperlessBilling': ['Yes', 'No', 'No'],
    'PaymentMethod': ['Electronic check', 'Mailed check', 'Bank transfer (automatic)'],
    'MonthlyCharges': [50.0, 100.0, 20.0],
    'TotalCharges': [50.0, 2400.0, 1440.0],
    'Churn': [1, 0, 0]
}

df = pd.DataFrame(data)
X = df.drop(columns=["Churn"])
y = df["Churn"]

obj_cols = [c for c in X.select_dtypes(include="object").columns]
X_processed = pd.get_dummies(X, columns=obj_cols)

model = LogisticRegression(max_iter=1000)
model.fit(X_processed, y)

joblib.dump(model, "models/churn_model.pkl")
print("Dummy model generated successfully at models/churn_model.pkl")
