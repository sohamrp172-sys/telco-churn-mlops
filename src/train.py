import argparse
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

MODEL_PATH = "models/churn_model.pkl"
EXPERIMENT_NAME = "churn-prediction"


def build_model(model_type: str):
    if model_type == "lr":
        return LogisticRegression(max_iter=1000)
    if model_type == "rf":
        return RandomForestClassifier(n_estimators=100, random_state=42)
    raise ValueError(f"Unknown model-type '{model_type}'. Choose 'lr' or 'rf'.")


def train(input_path: str, model_type: str, run_name: str) -> None:
    df = pd.read_csv(input_path)
    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name=run_name):
        model = build_model(model_type)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        roc_auc = roc_auc_score(y_test, y_proba)

        mlflow.log_param("model_type", model_type)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("roc_auc", roc_auc)
        mlflow.sklearn.log_model(model, artifact_path="model")

        joblib.dump(model, MODEL_PATH)

        print(f"  Accuracy : {accuracy:.4f}")
        print(f"  F1 Score : {f1:.4f}")
        print(f"  ROC AUC  : {roc_auc:.4f}")
        print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train telco churn classifier")
    parser.add_argument("--input", required=True, help="Path to processed CSV")
    parser.add_argument(
        "--model-type", required=True, choices=["lr", "rf"], help="lr or rf"
    )
    parser.add_argument("--run-name", required=True, help="MLflow run name")
    args = parser.parse_args()

    train(args.input, args.model_type, args.run_name)
