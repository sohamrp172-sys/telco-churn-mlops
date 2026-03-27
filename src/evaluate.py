import argparse
import sys

import joblib
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)


def evaluate(model_path: str, input_path: str) -> None:
    model = joblib.load(model_path)

    df = pd.read_csv(input_path)
    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]

    print("Classification Report:")
    print(classification_report(y, y_pred, target_names=["No Churn", "Churn"]))

    print("Confusion Matrix:")
    cm = confusion_matrix(y, y_pred)
    print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

    roc_auc = roc_auc_score(y, y_proba)
    print(f"\nROC-AUC Score: {roc_auc:.4f}")

    f1 = f1_score(y, y_pred, average="weighted")
    if f1 < 0.70:
        print(f"\nFAIL: F1 score {f1:.4f} is below threshold 0.70")
        sys.exit(1)

    print(f"\nPASS: F1 score {f1:.4f} meets threshold 0.70")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate telco churn model")
    parser.add_argument("--model-path", required=True, help="Path to saved .pkl model")
    parser.add_argument("--input", required=True, help="Path to processed CSV")
    args = parser.parse_args()

    evaluate(args.model_path, args.input)
