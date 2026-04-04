import argparse
import sys

import joblib
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    accuracy_score,
)


def evaluate(model_path: str, input_path: str) -> None:
    model = joblib.load(model_path)

    df = pd.read_csv(input_path)
    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]

    accuracy  = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, average="weighted", zero_division=0)
    recall    = recall_score(y, y_pred, average="weighted", zero_division=0)
    f1        = f1_score(y, y_pred, average="weighted")
    roc_auc   = roc_auc_score(y, y_proba)

    print("\n" + "=" * 50)
    print("        MODEL EVALUATION REPORT")
    print("=" * 50)
    print(f"  Accuracy  : {accuracy:.4f}  ({accuracy*100:.2f}%)")
    print(f"  Precision : {precision:.4f}")
    print(f"  Recall    : {recall:.4f}")
    print(f"  F1 Score  : {f1:.4f}")
    print(f"  ROC-AUC   : {roc_auc:.4f}")
    print("=" * 50)

    print("\nClassification Report:")
    print(classification_report(y, y_pred, target_names=["No Churn", "Churn"]))

    print("Confusion Matrix:")
    cm = confusion_matrix(y, y_pred)
    print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

    THRESHOLD = 0.80
    if f1 < THRESHOLD:
        print(f"\nFAIL: F1 score {f1:.4f} is below threshold {THRESHOLD}")
        sys.exit(1)

    print(f"\nPASS: F1 score {f1:.4f} meets threshold {THRESHOLD}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate telco churn model")
    parser.add_argument("--model-path", required=True, help="Path to saved .pkl model")
    parser.add_argument("--input", required=True, help="Path to processed CSV")
    args = parser.parse_args()

    evaluate(args.model_path, args.input)
