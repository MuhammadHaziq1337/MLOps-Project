"""Unit tests for model training module."""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge

from src.models.train import evaluate_model, train_model, tune_hyperparameters


class TestModelTraining(unittest.TestCase):
    """Tests for model training functions."""
    
    def setUp(self):
        """Set up test data."""
        # Create test data for classification
        np.random.seed(42)
        self.X_train_cls = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100)
        })
        self.y_train_cls = pd.Series(np.random.randint(0, 2, 100))
        
        self.X_test_cls = pd.DataFrame({
            'feature1': np.random.rand(20),
            'feature2': np.random.rand(20)
        })
        self.y_test_cls = pd.Series(np.random.randint(0, 2, 20))
        
        # Create test data for regression
        self.X_train_reg = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100)
        })
        self.y_train_reg = pd.Series(np.random.rand(100))
        
        self.X_test_reg = pd.DataFrame({
            'feature1': np.random.rand(20),
            'feature2': np.random.rand(20)
        })
        self.y_test_reg = pd.Series(np.random.rand(20))
    
    @patch('mlflow.start_run')
    @patch('mlflow.log_param')
    @patch('mlflow.sklearn.log_model')
    @patch('mlflow.end_run')
    def test_train_classification_model(
        self, mock_end_run, mock_log_model, mock_log_param, mock_start_run
    ):
        """Test training a classification model."""
        # Mock MLflow context
        mock_start_run.return_value = MagicMock()
        
        # Train a logistic regression model
        model = train_model(
            self.X_train_cls,
            self.y_train_cls,
            model_type='classification',
            model_params={'C': 1.0},
            use_mlflow=True
        )
        
        # Check that the model is a LogisticRegression
        self.assertIsInstance(model, LogisticRegression)
        
        # Check that MLflow functions were called
        mock_start_run.assert_called_once()
        mock_log_param.assert_any_call('model_type', 'classification')
        mock_log_param.assert_any_call('C', 1.0)
        mock_log_model.assert_called_once()
        mock_end_run.assert_called_once()
    
    @patch('mlflow.start_run')
    @patch('mlflow.log_param')
    @patch('mlflow.sklearn.log_model')
    @patch('mlflow.end_run')
    def test_train_regression_model(
        self, mock_end_run, mock_log_model, mock_log_param, mock_start_run
    ):
        """Test training a regression model."""
        # Mock MLflow context
        mock_start_run.return_value = MagicMock()
        
        # Train a ridge regression model
        model = train_model(
            self.X_train_reg,
            self.y_train_reg,
            model_type='regression',
            model_params={'alpha': 0.5},
            use_mlflow=True
        )
        
        # Check that the model is a Ridge regressor
        self.assertIsInstance(model, Ridge)
        
        # Check that MLflow functions were called
        mock_start_run.assert_called_once()
        mock_log_param.assert_any_call('model_type', 'regression')
        mock_log_param.assert_any_call('alpha', 0.5)
        mock_log_model.assert_called_once()
        mock_end_run.assert_called_once()
    
    @patch('mlflow.start_run')
    @patch('mlflow.log_param')
    @patch('mlflow.sklearn.log_model')
    @patch('mlflow.end_run')
    def test_train_random_forest(
        self, mock_end_run, mock_log_model, mock_log_param, mock_start_run
    ):
        """Test training a random forest model."""
        # Mock MLflow context
        mock_start_run.return_value = MagicMock()
        
        # Train a random forest classifier
        model = train_model(
            self.X_train_cls,
            self.y_train_cls,
            model_type='classification',
            model_params={'model_name': 'random_forest', 'n_estimators': 10},
            use_mlflow=True
        )
        
        # Check that the model is a RandomForestClassifier
        self.assertIsInstance(model, RandomForestClassifier)
        self.assertEqual(model.n_estimators, 10)
        
        # Train a random forest regressor
        model = train_model(
            self.X_train_reg,
            self.y_train_reg,
            model_type='regression',
            model_params={'model_name': 'random_forest', 'n_estimators': 15},
            use_mlflow=True
        )
        
        # Check that the model is a RandomForestRegressor
        self.assertIsInstance(model, RandomForestRegressor)
        self.assertEqual(model.n_estimators, 15)
    
    @patch('mlflow.start_run')
    @patch('mlflow.log_metric')
    def test_evaluate_classification_model(self, mock_log_metric, mock_start_run):
        """Test evaluating a classification model."""
        # Mock MLflow context
        mock_start_run.return_value = MagicMock()
        mock_start_run.return_value.__enter__.return_value = MagicMock()
        
        # Train a simple model
        model = LogisticRegression()
        model.fit(self.X_train_cls, self.y_train_cls)
        
        # Evaluate the model
        metrics = evaluate_model(
            model,
            self.X_test_cls,
            self.y_test_cls,
            model_type='classification',
            use_mlflow=True
        )
        
        # Check that metrics are returned
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1', metrics)
        
        # Check that MLflow functions were called
        mock_start_run.assert_called_once()
        # Four metrics should be logged
        self.assertEqual(mock_log_metric.call_count, 4)
    
    @patch('mlflow.start_run')
    @patch('mlflow.log_metric')
    def test_evaluate_regression_model(self, mock_log_metric, mock_start_run):
        """Test evaluating a regression model."""
        # Mock MLflow context
        mock_start_run.return_value = MagicMock()
        mock_start_run.return_value.__enter__.return_value = MagicMock()
        
        # Train a simple model
        model = Ridge()
        model.fit(self.X_train_reg, self.y_train_reg)
        
        # Evaluate the model
        metrics = evaluate_model(
            model,
            self.X_test_reg,
            self.y_test_reg,
            model_type='regression',
            use_mlflow=True
        )
        
        # Check that metrics are returned
        self.assertIn('mse', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('r2', metrics)
        
        # Check that MLflow functions were called
        mock_start_run.assert_called_once()
        # Four metrics should be logged
        self.assertEqual(mock_log_metric.call_count, 4)
    
    @patch('mlflow.set_experiment')
    @patch('mlflow.start_run')
    @patch('mlflow.log_param')
    @patch('mlflow.log_metric')
    @patch('mlflow.sklearn.log_model')
    def test_tune_hyperparameters(
        self, mock_log_model, mock_log_metric, mock_log_param, mock_start_run,
        mock_set_experiment
    ):
        """Test hyperparameter tuning function."""
        # Mock MLflow context
        mock_start_run.return_value = MagicMock()
        mock_start_run.return_value.__enter__.return_value = MagicMock()
        
        # Define a simple parameter grid
        param_grid = {
            'C': [0.1, 1.0, 10.0],
            'solver': ['liblinear']
        }
        
        # Tune hyperparameters
        best_model, best_params = tune_hyperparameters(
            self.X_train_cls,
            self.y_train_cls,
            self.X_test_cls,
            self.y_test_cls,
            model_type='classification',
            param_grid=param_grid,
            cv=3,
            use_mlflow=True
        )
        
        # Check that a model and parameters are returned
        self.assertIsInstance(best_model, LogisticRegression)
        self.assertIn('C', best_params)
        self.assertIn('solver', best_params)
        
        # Check that MLflow functions were called
        mock_set_experiment.assert_called_once()
        mock_start_run.assert_called_once()
        self.assertGreater(mock_log_param.call_count, 0)
        self.assertGreater(mock_log_metric.call_count, 0)
        mock_log_model.assert_called_once()


if __name__ == '__main__':
    unittest.main() 