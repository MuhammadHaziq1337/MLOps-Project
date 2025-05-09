"""Unit tests for data preprocessing module."""

import os
import tempfile
import unittest

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.data.preprocessing import (
    clean_data, load_data, scale_features, split_data
)


class TestDataPreprocessing(unittest.TestCase):
    """Tests for data preprocessing functions."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test DataFrame
        self.df = pd.DataFrame({
            'numeric_col': [1, 2, np.nan, 4, 5],
            'categorical_col': ['A', 'B', 'C', np.nan, 'A'],
            'target': [0, 1, 0, 1, 0]
        })
        
        # Create a temporary CSV file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, 'test_data.csv')
        self.df.to_csv(self.temp_file, index=False)
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_load_data(self):
        """Test load_data function."""
        loaded_df = load_data(self.temp_file)
        
        # Check that the loaded DataFrame has the same shape and columns
        self.assertEqual(loaded_df.shape, self.df.shape)
        self.assertListEqual(list(loaded_df.columns), list(self.df.columns))
    
    def test_clean_data(self):
        """Test clean_data function."""
        cleaned_df = clean_data(self.df.copy())
        
        # Check that there are no missing values
        self.assertEqual(cleaned_df.isna().sum().sum(), 0)
        
        # Check that numeric missing values are filled with median
        self.assertEqual(cleaned_df.loc[2, 'numeric_col'], 3.0)  # Median of [1, 2, 4, 5]
        
        # Check that categorical missing values are filled with mode
        self.assertEqual(cleaned_df.loc[3, 'categorical_col'], 'A')  # Mode of ['A', 'B', 'C', 'A']
    
    def test_split_data(self):
        """Test split_data function."""
        # Create a clean DataFrame for splitting
        df = pd.DataFrame({
            'feature1': range(100),
            'feature2': range(100),
            'target': [i % 2 for i in range(100)]
        })
        
        X_train, X_test, y_train, y_test = split_data(
            df, 'target', test_size=0.2, random_state=42
        )
        
        # Check that the splits have the correct shapes
        self.assertEqual(X_train.shape[0], 80)  # 80% of 100
        self.assertEqual(X_test.shape[0], 20)   # 20% of 100
        self.assertEqual(y_train.shape[0], 80)
        self.assertEqual(y_test.shape[0], 20)
        
        # Check that 'target' is not in the feature DataFrames
        self.assertNotIn('target', X_train.columns)
        self.assertNotIn('target', X_test.columns)
    
    def test_scale_features(self):
        """Test scale_features function."""
        # Create DataFrames for scaling
        X_train = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [10, 20, 30, 40, 50]
        })
        
        X_test = pd.DataFrame({
            'feature1': [6, 7],
            'feature2': [60, 70]
        })
        
        X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
        
        # Check that the scaled DataFrames have the same shape
        self.assertEqual(X_train_scaled.shape, X_train.shape)
        self.assertEqual(X_test_scaled.shape, X_test.shape)
        
        # Check that the scaler is a StandardScaler
        self.assertIsInstance(scaler, StandardScaler)
        
        # Check that the mean of the scaled training data is approximately 0
        self.assertAlmostEqual(X_train_scaled['feature1'].mean(), 0, places=10)
        self.assertAlmostEqual(X_train_scaled['feature2'].mean(), 0, places=10)
        
        # Check that the standard deviation of the scaled training data is approximately 1
        self.assertAlmostEqual(X_train_scaled['feature1'].std(), 1, places=10)
        self.assertAlmostEqual(X_train_scaled['feature2'].std(), 1, places=10)


if __name__ == '__main__':
    unittest.main() 