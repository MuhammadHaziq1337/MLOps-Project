#!/usr/bin/env python
"""
Train a simple demo model for testing the MLOps pipeline.
"""
import os
import pickle
import warnings
warnings.filterwarnings('ignore')

import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Create directory if it doesn't exist
os.makedirs("models/latest", exist_ok=True)

# Load dataset
print("Loading Iris dataset...")
iris = load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
print("Training Random Forest model...")
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.4f}")

# Save model
print("Saving model...")
model_path = "models/latest/model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(model, f)

# Save some metadata
print("Saving MLmodel file...")
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
with open("models/latest/MLmodel", "w") as f:
    f.write(mlmodel_content)

print("Done! Model saved to models/latest/") 