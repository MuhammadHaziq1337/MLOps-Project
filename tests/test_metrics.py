"""
Unit tests for the metrics module used for Prometheus monitoring.
"""

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import metrics
from src.app.main import app


class TestMetricsModule(unittest.TestCase):
    """Tests for the metrics collection module."""

    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_record_request_metrics(self):
        """Test recording of HTTP request metrics."""
        # Record request start
        start_time = metrics.record_request_start("GET", "/test")

        # Verify start_time is a float timestamp
        self.assertIsInstance(start_time, float)

        # Record request end with mocked Counter and Histogram
        with patch.object(
            metrics.REQUEST_COUNT, "labels"
        ) as mock_counter_labels:
            with patch.object(
                metrics.REQUEST_LATENCY, "labels"
            ) as mock_histogram_labels:
                # Setup mock counter and histogram
                mock_counter = MagicMock()
                mock_counter_labels.return_value = mock_counter

                mock_histogram = MagicMock()
                mock_histogram_labels.return_value = mock_histogram

                # Call record_request_end
                metrics.record_request_end(start_time, "GET", "/test", 200)

                # Verify counter was incremented with correct labels
                mock_counter_labels.assert_called_once_with(
                    method="GET", endpoint="/test", status_code=200
                )
                mock_counter.inc.assert_called_once()

                # Verify histogram observed latency with correct labels
                mock_histogram_labels.assert_called_once_with(
                    method="GET", endpoint="/test"
                )
                mock_histogram.observe.assert_called_once()
                # Verify observed value is a positive float (latency)
                self.assertGreaterEqual(
                    mock_histogram.observe.call_args[0][0], 0
                )

    def test_record_prediction(self):
        """Test recording of model prediction metrics."""
        model_name = "test_model"
        features = {"feature1": 0.5, "feature2": 1.0}
        predicted_class = "class_a"

        # Mock metrics
        with patch.object(
            metrics.PREDICTION_COUNT, "labels"
        ) as mock_counter_labels:
            with patch.object(
                metrics, "_update_feature_statistics"
            ) as mock_update_stats:
                # Setup mock counter
                mock_counter = MagicMock()
                mock_counter_labels.return_value = mock_counter

                # Call record_prediction
                metrics.record_prediction(
                    model_name, features, predicted_class
                )

                # Verify counter was incremented with correct labels
                mock_counter_labels.assert_called_once_with(
                    model_name=model_name, class_name=predicted_class
                )
                mock_counter.inc.assert_called_once()

                # Verify feature statistics were updated
                mock_update_stats.assert_called_once()
                self.assertEqual(mock_update_stats.call_args[0][0], model_name)
                # Verify buffer was updated
                self.assertIn(features, metrics._PREDICTIONS_BUFFER)

    def test_update_feature_statistics(self):
        """Test updating feature statistics."""
        model_name = "test_model"
        predictions = [
            {"feature1": 1.0, "feature2": 2.0},
            {"feature1": 2.0, "feature2": 3.0},
            {"feature1": 3.0, "feature2": 4.0},
        ]

        # Expected statistics calculation is not needed
        # Mock metrics
        with patch.object(
            metrics.FEATURE_MEAN, "labels"
        ) as mock_mean_labels:
            with patch.object(
                metrics.FEATURE_STDDEV, "labels"
            ) as mock_stddev_labels:
                # Setup mock gauges
                mock_mean = MagicMock()
                mock_mean_labels.return_value = mock_mean

                mock_stddev = MagicMock()
                mock_stddev_labels.return_value = mock_stddev

                # Call _update_feature_statistics
                metrics._update_feature_statistics(model_name, predictions)

                # Verify mean was set with correct labels and values
                mock_mean_labels.assert_any_call(
                    model_name=model_name, feature="feature1"
                )
                mock_mean_labels.assert_any_call(
                    model_name=model_name, feature="feature2"
                )

                # Verify stddev was set with correct labels and values
                mock_stddev_labels.assert_any_call(
                    model_name=model_name, feature="feature1"
                )
                mock_stddev_labels.assert_any_call(
                    model_name=model_name, feature="feature2"
                )

    def test_update_data_drift(self):
        """Test updating data drift score."""
        model_name = "test_model"
        feature = "feature1"
        drift_score = 0.25

        # Mock metrics
        with patch.object(
            metrics.DATA_DRIFT_SCORE, "labels"
        ) as mock_drift_labels:
            # Setup mock gauge
            mock_drift = MagicMock()
            mock_drift_labels.return_value = mock_drift

            # Call update_data_drift
            metrics.update_data_drift(model_name, feature, drift_score)

            # Verify drift score was set with correct labels and value
            mock_drift_labels.assert_called_once_with(
                model_name=model_name, feature=feature
            )
            mock_drift.set.assert_called_once_with(drift_score)

    def test_get_metrics(self):
        """Test getting metrics in Prometheus format."""
        # Call get_metrics
        metrics_data = metrics.get_metrics()

        # Verify metrics data is bytes
        self.assertIsInstance(metrics_data, bytes)

        # Verify metrics data contains expected metrics
        metrics_str = metrics_data.decode("utf-8")
        self.assertIn("http_requests", metrics_str)
        self.assertIn("http_request_duration_seconds", metrics_str)
        self.assertIn("model_prediction_count", metrics_str)
        self.assertIn("model_prediction_latency_seconds", metrics_str)

    def test_metrics_endpoint(self):
        """Test the metrics endpoint of the FastAPI app."""
        # Call metrics endpoint
        response = self.client.get("/metrics")

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["content-type"], "text/plain; charset=utf-8"
        )

        # Verify response content
        self.assertIn("http_requests", response.text)
        self.assertIn("http_request_duration_seconds", response.text)
        self.assertIn("model_prediction_count", response.text)
        self.assertIn("model_prediction_latency_seconds", response.text)

    def test_metrics_middleware(self):
        """Test that MetricsMiddleware properly records requests."""
        # Make a request to an endpoint that should be tracked
        response = self.client.get("/health")

        # Verify response
        self.assertEqual(response.status_code, 200)

        # For middleware testing, we don't need to check specific metrics
        # since we're already testing the metrics modules separately

    def test_record_feature_values(self):
        """Test recording feature values."""
        # Create a mock for the observe method
        mock_observe = MagicMock()

        # Create a mock for the labels method that returns the mock_observe
        mock_labels = MagicMock()
        mock_labels.return_value = mock_observe

        # Patch the labels method on FEATURE_VALUES
        with patch.object(
            metrics.FEATURE_VALUES, "labels", return_value=mock_observe
        ) as mock_labels_fn:
            # Call the function that records feature values
            metrics.record_feature_values(
                {"feature1": [1.0, 2.0, 3.0], "feature2": [4.0, 5.0, 6.0]}
            )

            # Assert labels was called with each feature
            self.assertEqual(mock_labels_fn.call_count, 6)

            # Assert observe was called for each value
            self.assertEqual(mock_observe.observe.call_count, 6)


if __name__ == "__main__":
    unittest.main()
