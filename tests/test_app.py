"""Unit tests for the FastAPI application."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app.main import app

class TestApp(unittest.TestCase):
    """Tests for the FastAPI application."""
    
    def setUp(self):
        """Set up test client and mock model."""
        self.client = TestClient(app)
    
    @patch('src.app.main.model')
    def test_health_check_model_loaded(self, mock_model):
        """Test health check endpoint when model is loaded."""
        # Set up mock model
        mock_model.return_value = MagicMock()
        
        # Call health check endpoint
        response = self.client.get("/health")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "healthy", "message": "Model is loaded and ready for inference"}
        )
    
    @patch('src.app.main.model', None)
    def test_health_check_model_not_loaded(self):
        """Test health check endpoint when model is not loaded."""
        # Call health check endpoint
        response = self.client.get("/health")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "error", "message": "Model not loaded"}
        )
    
    @patch('src.app.main.model')
    def test_predict_binary_classification(self, mock_model):
        """Test prediction endpoint for binary classification."""
        # Set up mock model
        mock_model.predict.return_value = [1]  # Binary classification prediction
        mock_model.predict_proba.return_value = [[0.2, 0.8]]  # Classification probabilities
        
        # Prepare input data
        input_data = {
            "features": {
                "feature1": 0.5,
                "feature2": 0.7
            }
        }
        
        # Call predict endpoint
        response = self.client.post(
            "/predict",
            json=input_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["prediction"], 1)
        self.assertAlmostEqual(result["probability"], 0.8)
        
        # Check that the model was called with the correct data
        mock_model.predict.assert_called_once()
        mock_model.predict_proba.assert_called_once()
    
    @patch('src.app.main.model')
    def test_predict_multiclass_classification(self, mock_model):
        """Test prediction endpoint for multiclass classification."""
        # Set up mock model
        mock_model.predict.return_value = [2]  # Multiclass classification prediction
        mock_model.predict_proba.return_value = [[0.1, 0.2, 0.7]]  # Multiclass probabilities
        
        # Prepare input data
        input_data = {
            "features": {
                "feature1": 0.5,
                "feature2": 0.7
            }
        }
        
        # Call predict endpoint
        response = self.client.post(
            "/predict",
            json=input_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["prediction"], 2)
        self.assertEqual(result["confidence"], {"0": 0.1, "1": 0.2, "2": 0.7})
        
        # Check that the model was called with the correct data
        mock_model.predict.assert_called_once()
        mock_model.predict_proba.assert_called_once()
    
    @patch('src.app.main.model')
    def test_predict_regression(self, mock_model):
        """Test prediction endpoint for regression."""
        # Set up mock model
        mock_model.predict.return_value = [3.14]  # Regression prediction
        # Regression models don't have predict_proba
        delattr(mock_model, 'predict_proba')
        
        # Prepare input data
        input_data = {
            "features": {
                "feature1": 0.5,
                "feature2": 0.7
            }
        }
        
        # Call predict endpoint
        response = self.client.post(
            "/predict",
            json=input_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["prediction"], 3.14)
        self.assertNotIn("probability", result)
        self.assertNotIn("confidence", result)
        
        # Check that the model was called with the correct data
        mock_model.predict.assert_called_once()
    
    @patch('src.app.main.model', None)
    def test_predict_model_not_loaded(self):
        """Test prediction endpoint when model is not loaded."""
        # Prepare input data
        input_data = {
            "features": {
                "feature1": 0.5,
                "feature2": 0.7
            }
        }
        
        # Call predict endpoint
        response = self.client.post(
            "/predict",
            json=input_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Model not loaded"})
    
    @patch('src.app.main.model')
    @patch('src.app.main.os.environ')
    def test_model_info(self, mock_environ, mock_model):
        """Test model info endpoint."""
        # Set up environment variables
        mock_environ.get.side_effect = lambda key, default: {
            'MODEL_PATH': 'models/test_model',
            'MLFLOW_TRACKING_URI': 'http://test-mlflow:5000'
        }.get(key, default)
        
        # Call model info endpoint
        response = self.client.get("/model/info")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["model_path"], "models/test_model")
        self.assertEqual(result["mlflow_tracking_uri"], "http://test-mlflow:5000")


if __name__ == '__main__':
    unittest.main() 