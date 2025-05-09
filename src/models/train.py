"""Model training utilities."""

import logging
import os
from typing import Any, Dict, Optional, Tuple

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error,
                           mean_squared_error, precision_score, r2_score,
                           recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV

logger = logging.getLogger(__name__)


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_type: str = "classification",
    model_params: Optional[Dict[str, Any]] = None,
    use_mlflow: bool = True,
    experiment_name: str = "default",
) -> Any:
    """
    Train a model on the given data.
    
    Args:
        X_train: Training data features
        y_train: Training data target
        model_type: Type of model to train ('classification' or 'regression')
        model_params: Parameters to pass to the model constructor
        use_mlflow: Whether to log metrics to MLflow
        experiment_name: MLflow experiment name
        
    Returns:
        Trained model
    """
    logger.info(f"Training {model_type} model")
    
    if model_params is None:
        model_params = {}
    
    if use_mlflow:
        mlflow.set_experiment(experiment_name)
        mlflow.start_run()
        
        # Log parameters
        mlflow.log_param("model_type", model_type)
        for param, value in model_params.items():
            mlflow.log_param(param, value)
    
    # Select model based on type
    if model_type == "classification":
        if model_params.get("model_name") == "random_forest":
            params = {k: v for k, v in model_params.items() if k != "model_name"}
            model = RandomForestClassifier(**params)
        else:
            model = LogisticRegression(**model_params)
    elif model_type == "regression":
        if model_params.get("model_name") == "random_forest":
            params = {k: v for k, v in model_params.items() if k != "model_name"}
            model = RandomForestRegressor(**params)
        else:
            model = Ridge(**model_params)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Train model
    model.fit(X_train, y_train)
    
    if use_mlflow:
        # Log model to MLflow
        mlflow.sklearn.log_model(model, "model")
        mlflow.end_run()
    
    return model


def evaluate_model(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_type: str = "classification",
    use_mlflow: bool = True,
) -> Dict[str, float]:
    """
    Evaluate a trained model on test data.
    
    Args:
        model: Trained model
        X_test: Test data features
        y_test: Test data target
        model_type: Type of model ('classification' or 'regression')
        use_mlflow: Whether to log metrics to MLflow
        
    Returns:
        Dictionary of evaluation metrics
    """
    logger.info(f"Evaluating {model_type} model")
    
    y_pred = model.predict(X_test)
    
    if model_type == "classification":
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="weighted"),
            "recall": recall_score(y_test, y_pred, average="weighted"),
            "f1": f1_score(y_test, y_pred, average="weighted"),
        }
        
        # Add ROC AUC if model supports predict_proba
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)
            if len(np.unique(y_test)) == 2:  # Binary classification
                metrics["roc_auc"] = roc_auc_score(y_test, y_prob[:, 1])
    
    elif model_type == "regression":
        metrics = {
            "mse": mean_squared_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "mae": mean_absolute_error(y_test, y_pred),
            "r2": r2_score(y_test, y_pred),
        }
    
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Log metrics to MLflow
    if use_mlflow:
        with mlflow.start_run():
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
    
    return metrics


def tune_hyperparameters(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_type: str = "classification",
    param_grid: Optional[Dict[str, Any]] = None,
    cv: int = 5,
    use_mlflow: bool = True,
    experiment_name: str = "hyperparameter_tuning",
) -> Tuple[Any, Dict[str, Any]]:
    """
    Perform hyperparameter tuning using cross-validation.
    
    Args:
        X_train: Training data features
        y_train: Training data target
        X_test: Test data features
        y_test: Test data target
        model_type: Type of model ('classification' or 'regression')
        param_grid: Grid of hyperparameters to search
        cv: Number of cross-validation folds
        use_mlflow: Whether to log metrics to MLflow
        experiment_name: MLflow experiment name
        
    Returns:
        Tuple of (best_model, best_params)
    """
    logger.info(f"Performing hyperparameter tuning for {model_type} model")
    
    if param_grid is None:
        if model_type == "classification":
            param_grid = {
                "C": [0.01, 0.1, 1.0, 10.0],
                "solver": ["liblinear", "lbfgs"],
            }
            base_model = LogisticRegression()
        else:  # regression
            param_grid = {
                "alpha": [0.01, 0.1, 1.0, 10.0],
                "solver": ["auto", "svd", "cholesky"],
            }
            base_model = Ridge()
    
    grid_search = GridSearchCV(
        base_model,
        param_grid,
        cv=cv,
        scoring="accuracy" if model_type == "classification" else "neg_mean_squared_error",
        n_jobs=-1,
    )
    
    # Fit the grid search
    grid_search.fit(X_train, y_train)
    
    # Get best model and parameters
    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    
    # Evaluate the best model
    metrics = evaluate_model(best_model, X_test, y_test, model_type, use_mlflow=False)
    
    if use_mlflow:
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run():
            # Log best parameters
            for param, value in best_params.items():
                mlflow.log_param(param, value)
            
            # Log evaluation metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log best model
            mlflow.sklearn.log_model(best_model, "tuned_model")
    
    return best_model, best_params 