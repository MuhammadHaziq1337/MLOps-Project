"""Tests for the data processing module."""

import os
import tempfile
from unittest import TestCase, mock

import pandas as pd
import pytest

from src.data.process import get_dataset, process_data


class TestDataProcess(TestCase):
    """Tests for data processing functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create sample dataframe with simple data
        self.sample_df = pd.DataFrame(
            {
                "feature1": [1.0, 2.0, 3.0, 4.0, 5.0],
                "feature2": [0.1, 0.2, 0.3, 0.4, 0.5],
                "target": [0, 1, 0, 1, 0],
            }
        )

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @mock.patch("src.data.process.load_iris")
    def test_get_dataset_iris(self, mock_load_iris):
        """Test get_dataset function with iris dataset."""
        # Mock the iris dataset
        mock_iris = mock.Mock()
        mock_iris.data = [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]
        mock_iris.feature_names = [
            "feature1",
            "feature2",
            "feature3",
            "feature4",
        ]
        mock_iris.target = [0, 1]
        mock_load_iris.return_value = mock_iris

        # Call function
        output_dir = self.temp_dir.name
        df = get_dataset("iris", output_dir)

        # Check result
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 2  # 2 samples
        assert df.shape[1] == 5  # 4 features + 1 target
        assert "target" in df.columns

        # Check if CSV file was created
        assert os.path.exists(os.path.join(output_dir, "iris.csv"))

    @mock.patch("src.data.process.fetch_california_housing")
    def test_get_dataset_california_housing(self, mock_fetch_housing):
        """Test get_dataset function with california_housing dataset."""
        # Mock the housing dataset
        mock_housing = mock.Mock()
        mock_housing.data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        mock_housing.feature_names = ["feature1", "feature2", "feature3"]
        mock_housing.target = [10.0, 20.0]
        mock_fetch_housing.return_value = mock_housing

        # Call function
        output_dir = self.temp_dir.name
        df = get_dataset("california_housing", output_dir)

        # Check result
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 2  # 2 samples
        assert df.shape[1] == 4  # 3 features + 1 target
        assert "target" in df.columns

        # Check if CSV file was created
        assert os.path.exists(
            os.path.join(
                output_dir,
                "california_housing.csv"))

    def test_get_dataset_unknown(self):
        """Test get_dataset function with unknown dataset."""
        with pytest.raises(ValueError):
            get_dataset("unknown_dataset", self.temp_dir.name)

    @mock.patch("src.data.process.clean_data")
    @mock.patch("src.data.process.split_data")
    def test_process_data(self, mock_split_data, mock_clean_data):
        """Test process_data function."""
        # Mock the output of clean_data
        mock_clean_data.return_value = self.sample_df

        # Mock the output of split_data
        X_train = pd.DataFrame(
            {"feature1": [1.0, 2.0, 3.0], "feature2": [0.1, 0.2, 0.3]}
        )
        X_test = pd.DataFrame({"feature1": [4.0, 5.0], "feature2": [0.4, 0.5]})
        y_train = pd.Series([0, 1, 0], name="target")
        y_test = pd.Series([1, 0], name="target")
        mock_split_data.return_value = (X_train, X_test, y_train, y_test)

        # Call function
        output_dir = self.temp_dir.name
        process_data(self.sample_df, "test_dataset", output_dir)

        # Verify function calls
        mock_clean_data.assert_called_once_with(self.sample_df)
        mock_split_data.assert_called_once()

        # Check if files were created
        assert os.path.exists(
            os.path.join(
                output_dir,
                "test_dataset_X_train.csv"))
        assert os.path.exists(
            os.path.join(
                output_dir,
                "test_dataset_X_test.csv"))
        assert os.path.exists(
            os.path.join(
                output_dir,
                "test_dataset_y_train.csv"))
        assert os.path.exists(
            os.path.join(
                output_dir,
                "test_dataset_y_test.csv"))
