# API Documentation

This document provides information on how to use the MLOps project API.

## Overview

The API serves machine learning models trained on different datasets, with the default being the Iris flower dataset. It provides endpoints for health checking, model information, and making predictions.

## Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API.

**Response Example:**
```json
{
  "status": "healthy",
  "message": "Model is loaded and ready for inference"
}
```

### Model Information

```
GET /model/info
```

Returns information about the loaded model.

**Response Example:**
```json
{
  "model_path": "models",
  "model_type": "RandomForestClassifier",
  "mlflow_tracking_uri": "http://localhost:5000"
}
```

### Prediction

```
POST /predict
```

Makes a prediction using the loaded model.

**Request Body Example (Iris dataset):**
```json
{
  "features": {
    "sepal length (cm)": 5.1,
    "sepal width (cm)": 3.5,
    "petal length (cm)": 1.4,
    "petal width (cm)": 0.2
  }
}
```

**Response Example:**
```json
{
  "prediction": 0,
  "confidence": {
    "0": 1.0,
    "1": 0.0,
    "2": 0.0
  }
}
```

Where:
- `prediction`: The predicted class (0 = Setosa, 1 = Versicolor, 2 = Virginica for Iris dataset)
- `confidence`: Confidence scores for each class (if available)
- `probability`: Probability of the prediction (for binary classification)

## Error Handling

The API returns appropriate error responses with status codes and error messages.

**Example Error Response:**
```json
{
  "detail": "Prediction error: <error message>"
}
```

## Running the API

1. Process data:
```
python -m src.data.process --dataset iris
```

2. Train model:
```
python -m src.models.run_training --dataset iris
```

3. Start the API server:
```
python -m src.app.main
```

4. Access the Swagger UI for interactive documentation:
```
http://localhost:8000/docs
```

## Testing the API

You can test the API using the provided test script:

```
python test_prediction.py
```

Or directly using tools like curl, Postman, or the Python requests library.

## Deploying with Kubernetes

Refer to the Kubernetes documentation in the project for deployment instructions. 