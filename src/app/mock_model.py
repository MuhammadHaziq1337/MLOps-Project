"""Mock model module for testing."""

import os
import pickle
import numpy as np


class MockModel:
    """A mock model that always returns class 0."""

    def __init__(self):
        """Initialize mock model."""
        self.name = "mock_model"
        self.classes_ = [0, 1, 2]  # For iris dataset

    def predict(self, X):
        """Return mock predictions."""
        if isinstance(X, np.ndarray):
            return np.zeros(X.shape[0], dtype=int)
        else:
            try:
                return np.zeros(len(X), dtype=int)
            except TypeError:
                return np.array([0])

    def predict_proba(self, X):
        """Return mock probabilities."""
        if isinstance(X, np.ndarray):
            n_samples = X.shape[0]
        else:
            try:
                n_samples = len(X)
            except TypeError:
                n_samples = 1

        # Generate probabilities with high confidence for class 0
        probs = np.zeros((n_samples, 3))
        probs[:, 0] = 0.9  # Class 0
        probs[:, 1] = 0.05  # Class 1
        probs[:, 2] = 0.05  # Class 2
        return probs


def get_mock_model():
    """Get a mock model instance."""
    return MockModel()


def save_mock_model(path="models/latest"):
    """Save a mock model to disk."""
    os.makedirs(path, exist_ok=True)
    model = get_mock_model()

    # Save the model
    with open(os.path.join(path, "model.pkl"), "wb") as f:
        pickle.dump(model, f)

    # Save MLmodel file
    mlmodel_content = """
artifact_path: model
flavors:
  python_function:
    env:
      conda: conda.yaml
      virtualenv: python_env.yaml
    loader_module: mlflow.sklearn
    model_path: model.pkl
    predict_fn: predict
    python_version: 3.9.12
  sklearn:
    code: null
    pickled_model: model.pkl
    serialization_format: cloudpickle
    sklearn_version: 1.2.2
model_uuid: 12345678-1234-5678-1234-567812345678
utc_time_created: '2023-05-11 00:00:00.000000'
"""
    with open(os.path.join(path, "MLmodel"), "w") as f:
        f.write(mlmodel_content)

    return os.path.join(path, "model.pkl")
