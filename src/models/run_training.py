"""Main script to run model training."""

import argparse
import json
import logging
import os
import pickle

import pandas as pd

# Try to import MLflow, but continue if not available
try:
    import mlflow
    import mlflow.sklearn

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("Warning: MLflow not available. " "Will save model without MLflow tracking.")

from src.models.train import evaluate_model, train_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_data(dataset_name: str, data_dir: str = "data/processed") -> tuple:
    """
    Load processed data for training.

    Args:
        dataset_name: Name of the dataset
        data_dir: Directory containing processed data

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    logger.info(f"Loading processed data for {dataset_name} dataset")

    X_train = pd.read_csv(os.path.join(data_dir, f"{dataset_name}_X_train.csv"))
    X_test = pd.read_csv(os.path.join(data_dir, f"{dataset_name}_X_test.csv"))
    y_train = pd.read_csv(
        os.path.join(data_dir, f"{dataset_name}_y_train.csv")
    ).squeeze()
    y_test = pd.read_csv(os.path.join(data_dir, f"{dataset_name}_y_test.csv")).squeeze()

    logger.info(
        f"Loaded data with {X_train.shape[0]} training samples and "
        f"{X_test.shape[0]} test samples"
    )

    return X_train, X_test, y_train, y_test


def save_model(model, output_path: str) -> None:
    """
    Save trained model to disk.

    Args:
        model: Trained model
        output_path: Path to save the model
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:
        pickle.dump(model, f)

    logger.info(f"Model saved to: {output_path}")


def save_metrics(metrics: dict, output_path: str) -> None:
    """
    Save model metrics to a JSON file.

    Args:
        metrics: Dictionary of model metrics
        output_path: Path to save the metrics JSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Metrics saved to: {output_path}")


def main():
    """Main function to train models."""
    parser = argparse.ArgumentParser(description="Train machine learning model")
    parser.add_argument(
        "--dataset",
        type=str,
        default="iris",
        help="Dataset to use (iris or california_housing)",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="classification",
        help="Type of model to train (classification or regression)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/processed",
        help="Directory containing processed data",
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default="models",
        help="Directory to save trained model",
    )
    parser.add_argument(
        "--metrics-file",
        type=str,
        default="metrics/model_metrics.json",
        help="File to save model metrics",
    )
    parser.add_argument(
        "--use-mlflow",
        action="store_true",
        help="Whether to use MLflow for tracking",
    )

    args = parser.parse_args()

    logger.info(f"Training {args.model_type} model for {args.dataset} dataset")

    # Set model parameters based on dataset and model type
    if args.model_type == "classification":
        if args.dataset == "iris":
            model_params = {
                "model_name": "random_forest",
                "n_estimators": 100,
                "max_depth": 5,
                "random_state": 42,
            }
        else:
            model_params = {
                "C": 1.0,
                "solver": "lbfgs",
                "max_iter": 1000,
                "random_state": 42,
            }
    else:  # regression
        if args.dataset == "california_housing":
            model_params = {
                "model_name": "random_forest",
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42,
            }
        else:
            model_params = {"alpha": 1.0, "solver": "auto", "random_state": 42}

    # Load data
    X_train, X_test, y_train, y_test = load_data(args.dataset, args.data_dir)

    # Train model
    if args.use_mlflow:
        logger.info("Using MLflow for experiment tracking")
        mlflow.set_tracking_uri(
            os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
        )
        mlflow.set_experiment(f"{args.dataset}_{args.model_type}")

    model = train_model(
        X_train,
        y_train,
        model_type=args.model_type,
        model_params=model_params,
        use_mlflow=args.use_mlflow,
        experiment_name=f"{args.dataset}_{args.model_type}",
    )

    # Evaluate model
    metrics = evaluate_model(
        model,
        X_test,
        y_test,
        model_type=args.model_type,
        use_mlflow=args.use_mlflow,
    )

    # Log metrics
    for metric_name, metric_value in metrics.items():
        logger.info(f"{metric_name}: {metric_value:.4f}")

    # Save model
    model_path = os.path.join(
        args.model_dir, f"{args.dataset}_{args.model_type}_model.pkl"
    )
    save_model(model, model_path)

    # Save metrics to JSON file
    save_metrics(metrics, args.metrics_file)


if __name__ == "__main__":
    main()
