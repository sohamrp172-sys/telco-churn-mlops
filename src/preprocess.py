import argparse
import pandas as pd


def preprocess(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)
    print(f"Shape before: {df.shape}")

    df = df.drop(columns=["customerID"])

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())

    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    # ── Feature Engineering ───────────────────────────────────────────────────
    # Charge-per-month ratio: how much a customer pays relative to loyalty
    df["ChargesPerTenure"] = df["MonthlyCharges"] / (df["tenure"] + 1)

    # Has any add-on services (proxy for commitment)
    add_on_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]
    df["HasAddOns"] = df[add_on_cols].apply(
        lambda row: int(any(v == "Yes" for v in row)), axis=1
    )

    # Is on a long-term contract
    df["IsLongTermContract"] = df["Contract"].apply(
        lambda x: 1 if x in ["One year", "Two year"] else 0
    )

    # Auto-pay flag (reduces churn)
    df["AutoPay"] = df["PaymentMethod"].apply(
        lambda x: 1 if x in ["Bank transfer (automatic)", "Credit card (automatic)"] else 0
    )

    obj_cols = [c for c in df.select_dtypes(include="object").columns if c != "Churn"]
    df = pd.get_dummies(df, columns=obj_cols)

    df.to_csv(output_path, index=False)
    print(f"Shape after:  {df.shape}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess telco churn CSV")
    parser.add_argument("--input", required=True, help="Path to raw CSV")
    parser.add_argument("--output", required=True, help="Path for processed CSV")
    args = parser.parse_args()

    preprocess(args.input, args.output)
