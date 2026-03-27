import argparse
import pandas as pd


def preprocess(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)
    print(f"Shape before: {df.shape}")

    df = df.drop(columns=["customerID"])

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())

    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

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
