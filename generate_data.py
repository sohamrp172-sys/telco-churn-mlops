"""
Generates a realistic 2000-row Telco Churn dataset (telco_v1.csv)
matching the exact format expected by preprocess.py
"""
import random
import os
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

N = 2000

def generate_dataset(n):
    customer_ids = [f"C{str(i).zfill(5)}" for i in range(1, n+1)]

    gender = np.random.choice(["Male", "Female"], n)
    senior_citizen = np.random.choice([0, 1], n, p=[0.84, 0.16])
    partner = np.random.choice(["Yes", "No"], n)
    dependents = np.random.choice(["Yes", "No"], n, p=[0.30, 0.70])
    tenure = np.random.randint(0, 73, n)

    phone_service = np.random.choice(["Yes", "No"], n, p=[0.90, 0.10])
    multiple_lines = []
    for ps in phone_service:
        if ps == "No":
            multiple_lines.append("No phone service")
        else:
            multiple_lines.append(np.random.choice(["Yes", "No"]))

    internet_service = np.random.choice(["DSL", "Fiber optic", "No"], n, p=[0.34, 0.44, 0.22])

    online_security, online_backup, device_protection, tech_support = [], [], [], []
    streaming_tv, streaming_movies = [], []
    for inet in internet_service:
        if inet == "No":
            online_security.append("No internet service")
            online_backup.append("No internet service")
            device_protection.append("No internet service")
            tech_support.append("No internet service")
            streaming_tv.append("No internet service")
            streaming_movies.append("No internet service")
        else:
            online_security.append(np.random.choice(["Yes", "No"]))
            online_backup.append(np.random.choice(["Yes", "No"]))
            device_protection.append(np.random.choice(["Yes", "No"]))
            tech_support.append(np.random.choice(["Yes", "No"]))
            streaming_tv.append(np.random.choice(["Yes", "No"]))
            streaming_movies.append(np.random.choice(["Yes", "No"]))

    contract = np.random.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.24, 0.21])
    paperless_billing = np.random.choice(["Yes", "No"], n, p=[0.59, 0.41])
    payment_method = np.random.choice(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        n, p=[0.34, 0.23, 0.22, 0.21]
    )

    monthly_charges = []
    for inet in internet_service:
        base = 20 if inet == "No" else (50 if inet == "DSL" else 80)
        monthly_charges.append(round(base + np.random.uniform(-5, 25), 2))

    total_charges = []
    for i in range(n):
        t = tenure[i]
        mc = monthly_charges[i]
        if t == 0:
            total_charges.append(" ")
        else:
            total_charges.append(str(round(mc * t + np.random.uniform(-50, 50), 2)))

    churn = []
    for i in range(n):
        prob = 0.15
        if contract[i] == "Month-to-month":
            prob += 0.25
        elif contract[i] == "One year":
            prob += 0.05
        if internet_service[i] == "Fiber optic":
            prob += 0.15
        if tenure[i] < 12:
            prob += 0.20
        if tenure[i] > 60:
            prob -= 0.15
        if tech_support[i] == "Yes":
            prob -= 0.10
        if online_security[i] == "Yes":
            prob -= 0.08
        if payment_method[i] == "Electronic check":
            prob += 0.10
        prob = max(0.01, min(0.98, prob))
        churn.append("Yes" if np.random.rand() < prob else "No")

    df = pd.DataFrame({
        "customerID": customer_ids,
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "Churn": churn,
    })
    return df

os.makedirs("data/raw", exist_ok=True)

df = generate_dataset(N)
df.to_csv("data/raw/telco_v1.csv", index=False)

churn_rate = (df["Churn"] == "Yes").mean() * 100
print(f"Dataset generated successfully!")
print(f"   Rows     : {len(df)}")
print(f"   Columns  : {len(df.columns)}")
print(f"   Churn %  : {churn_rate:.1f}%")
print(f"   Saved to : data/raw/telco_v1.csv")
