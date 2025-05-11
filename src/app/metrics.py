"""
Prometheus metrics for ML model monitoring.

This module provides metric collectors for monitoring ML model
performance and behavior.
"""

import time
from typing import Dict, List

from prometheus_client import REGISTRY, Counter, Gauge, Histogram, Summary
from prometheus_client.openmetrics.exposition import generate_latest

# HTTP request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

# ML model metrics
PREDICTION_COUNT = Counter(
    "model_prediction_count",
    "Number of predictions by class",
    ["model_name", "class_name"],
)

FEATURE_VALUES = Histogram(
    "model_feature_values",
    "Raw values of features observed in predictions",
    ["feature"],
)

FEATURE_MEAN = Gauge(
    "prediction_feature_mean",
    "Mean value of each feature in predictions",
    ["model_name", "feature"],
)

FEATURE_STDDEV = Gauge(
    "prediction_feature_stddev",
    "Standard deviation of each feature in predictions",
    ["model_name", "feature"],
)

PREDICTION_LATENCY = Summary(
    "model_prediction_latency_seconds",
    "Time taken for model to make predictions",
    ["model_name"],
)

DATA_DRIFT_SCORE = Gauge(
    "model_data_drift_score",
    "Measure of drift between training and prediction data",
    ["model_name", "feature"],
)

# Last predictions buffer (for computing statistics)
_PREDICTIONS_BUFFER = []
_BUFFER_SIZE = 100


def record_request_start(method: str, endpoint: str) -> float:
    """
    Record the start of an HTTP request and return the start time.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Request endpoint/path

    Returns:
        Start time for latency calculation
    """
    return time.time()


def record_request_end(
    start_time: float, method: str, endpoint: str, status_code: int
) -> None:
    """
    Record the end of an HTTP request and update metrics.

    Args:
        start_time: Request start time from record_request_start
        method: HTTP method (GET, POST, etc.)
        endpoint: Request endpoint/path
        status_code: Response status code
    """
    REQUEST_COUNT.labels(
        method=method, endpoint=endpoint, status_code=status_code
    ).inc()

    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)


def record_prediction(
    model_name: str, features: Dict[str, float], predicted_class: str
) -> None:
    """
    Record a model prediction and update metrics.

    Args:
        model_name: Name of the model making the prediction
        features: Dictionary of feature name to value
        predicted_class: Predicted class label
    """
    PREDICTION_COUNT.labels(
        model_name=model_name,
        class_name=predicted_class).inc()

    _PREDICTIONS_BUFFER.append(features)
    while len(_PREDICTIONS_BUFFER) > _BUFFER_SIZE:
        _PREDICTIONS_BUFFER.pop(0)

    _update_feature_statistics(model_name, _PREDICTIONS_BUFFER)

    PREDICTION_LATENCY.labels(model_name=model_name).observe(0.001)


def _update_feature_statistics(
    model_name: str, predictions: List[Dict[str, float]]
) -> None:
    """
    Update feature statistics based on recent predictions.

    Args:
        model_name: Name of the model
        predictions: List of feature dictionaries from recent predictions
    """
    if not predictions:
        return

    feature_values = {}
    for feature_name in predictions[0].keys():
        feature_values[feature_name] = [
            p.get(feature_name, 0)
            for p in predictions
            if feature_name in p
        ]

    for feature_name, values in feature_values.items():
        if not values:
            continue

        mean_value = sum(values) / len(values)
        FEATURE_MEAN.labels(
            model_name=model_name, feature=feature_name
        ).set(mean_value)

        if len(values) > 1:
            variance = sum((x - mean_value) ** 2 for x in values) / len(values)
            stddev = variance**0.5
            FEATURE_STDDEV.labels(
                model_name=model_name, feature=feature_name
            ).set(stddev)


def update_data_drift(model_name: str, feature: str,
                      drift_score: float) -> None:
    """
    Update the data drift score for a specific feature.

    Args:
        model_name: Name of the model
        feature: Feature name
        drift_score: Measure of drift (0-1, where 0 is no drift)
    """
    DATA_DRIFT_SCORE.labels(
        model_name=model_name,
        feature=feature).set(drift_score)


def get_metrics() -> bytes:
    """
    Generate Prometheus metrics output.

    Returns:
        Prometheus metrics formatted as bytes
    """
    return generate_latest(REGISTRY)


def record_feature_values(features_dict: Dict[str, List[float]]) -> None:
    """
    Record feature values directly for monitoring.

    Args:
        features_dict: Dictionary mapping feature names to lists of values
    """
    for feature_name, values in features_dict.items():
        for value in values:
            FEATURE_VALUES.labels(feature=feature_name).observe(value)
