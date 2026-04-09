import argparse
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split

MODEL_PATH = "models/churn_model_render.pkl"
EXPERIMENT_NAME = "churn-prediction"


def build_model(model_type: str):
    if model_type == "lr":
        return LogisticRegression(max_iter=1000, class_weight="balanced")
    if model_type == "rf":
        return RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_split=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
    if model_type == "gb":
        return GradientBoostingClassifier(
            n_estimators=400,
            learning_rate=0.08,
            max_depth=6,
            min_samples_split=5,
            subsample=0.85,
            max_features="sqrt",
            random_state=42,
        )
    raise ValueError(f"Unknown model-type '{model_type}'. Choose 'lr', 'rf', or 'gb'.")


def train(input_path: str, model_type: str, run_name: str) -> None:
    df = pd.read_csv(input_path)
    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name=run_name):
        model = build_model(model_type)

        # Hyperparameter tuning for Random Forest
        if model_type == "rf":
            print("  Running GridSearchCV for Random Forest...")
            param_grid = {
                "n_estimators": [200, 300],
                "max_depth": [10, 15, None],
                "min_samples_split": [2, 5],
            }
            grid_search = GridSearchCV(
                RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1),
                param_grid,
                cv=3,
                scoring="f1_weighted",
                n_jobs=-1,
            )
            grid_search.fit(X_train, y_train)
            model = grid_search.best_estimator_
            print(f"  Best params: {grid_search.best_params_}")
            mlflow.log_params(grid_search.best_params_)
        else:
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("test_size", 0.2)
            model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        accuracy  = accuracy_score(y_test, y_pred)
        f1        = f1_score(y_test, y_pred, average="weighted")
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall    = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        roc_auc   = roc_auc_score(y_test, y_proba)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("roc_auc", roc_auc)
        mlflow.sklearn.log_model(model, artifact_path="model")

        joblib.dump(model, MODEL_PATH)

        print(f"\n{'='*45}")
        print(f"  Model     : {model_type.upper()}")
        print(f"  Accuracy  : {accuracy:.4f}  ({accuracy*100:.2f}%)")
        print(f"  Precision : {precision:.4f}")
        print(f"  Recall    : {recall:.4f}")
        print(f"  F1 Score  : {f1:.4f}")
        print(f"  ROC AUC   : {roc_auc:.4f}")
        print(f"{'='*45}")
        print(f"  Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train telco churn classifier")
    parser.add_argument("--input", required=True, help="Path to processed CSV")
    parser.add_argument(
        "--model-type",
        required=True,
        choices=["lr", "rf", "gb"],
        help="lr (Logistic Regression), rf (Random Forest), or gb (Gradient Boosting)",
    )
    parser.add_argument("--run-name", required=True, help="MLflow run name")
    args = parser.parse_args()

    train(args.input, args.model_type, args.run_name)
