"""Tests for the data versioning functionality."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from scripts.data_versioning import (create_pipeline, init_dvc, pull_dataset,
                                     run_dvc_command, tag_dataset_version,
                                     track_dataset, update_dataset)


class TestDataVersioning(unittest.TestCase):
    """Test cases for data versioning functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create a sample dataset
        self.dataset_path = os.path.join(self.test_dir, "test_dataset.csv")
        df = pd.DataFrame(
            {"feature1": [1, 2, 3], "feature2": [4, 5, 6], "target": [0, 1, 0]}
        )
        df.to_csv(self.dataset_path, index=False)

    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    @patch("subprocess.run")
    def test_run_dvc_command(self, mock_run):
        """Test running a DVC command."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Command executed successfully"
        mock_run.return_value = mock_result

        # Test successful command
        result = run_dvc_command(["init"])
        self.assertTrue(result)
        mock_run.assert_called_once()

        # Test failed command
        mock_run.reset_mock()
        mock_result.returncode = 1
        mock_result.stderr = "Command failed"
        result = run_dvc_command(["invalid-command"], check=False)
        self.assertFalse(result)

    @patch("scripts.data_versioning.run_dvc_command")
    @patch("os.path.exists")
    def test_init_dvc(self, mock_exists, mock_run_cmd):
        """Test initializing DVC."""
        # Test when .dvc already exists
        mock_exists.return_value = True
        result = init_dvc()
        self.assertTrue(result)
        mock_run_cmd.assert_not_called()

        # Test when .dvc doesn't exist
        mock_exists.return_value = False
        mock_run_cmd.return_value = True
        result = init_dvc()
        self.assertTrue(result)
        mock_run_cmd.assert_called_once_with(["init"])

        # Test force initialization
        mock_exists.return_value = True
        mock_run_cmd.reset_mock()
        result = init_dvc(force=True)
        self.assertTrue(result)
        mock_run_cmd.assert_called_once_with(["init"])

    @patch("scripts.data_versioning.run_dvc_command")
    @patch("subprocess.run")
    def test_track_dataset(self, mock_subprocess_run, mock_run_cmd):
        """Test tracking a dataset."""
        # Setup mocks
        mock_run_cmd.return_value = True
        mock_subprocess_run.return_value.returncode = 0

        # Create a dummy .dvc file to simulate successful DVC add
        dvc_file = f"{self.dataset_path}.dvc"
        with open(dvc_file, "w") as f:
            f.write("dummy dvc file")

        # Test successful tracking
        result = track_dataset(self.dataset_path, "Initial dataset")
        self.assertTrue(result)
        mock_run_cmd.assert_called_once_with(["add", self.dataset_path])
        mock_subprocess_run.assert_called()

        # Test with non-existent dataset
        mock_run_cmd.reset_mock()
        mock_subprocess_run.reset_mock()
        result = track_dataset("non_existent_dataset.csv")
        self.assertFalse(result)
        mock_run_cmd.assert_not_called()

    @patch("scripts.data_versioning.run_dvc_command")
    def test_tag_dataset_version(self, mock_run_cmd):
        """Test tagging a dataset version."""
        # Create a dummy .dvc file
        dvc_file = f"{self.dataset_path}.dvc"
        with open(dvc_file, "w") as f:
            f.write("dummy dvc file")

        # Test successful tagging
        mock_run_cmd.return_value = True
        result = tag_dataset_version(self.dataset_path, "v1.0", "Version 1.0")
        self.assertTrue(result)
        mock_run_cmd.assert_called_once_with(
            [
                "tag",
                "add",
                "-d",
                self.dataset_path,
                "v1.0",
                "-m",
                "Version 1.0",
            ]
        )

        # Test with non-existent DVC file
        result = tag_dataset_version("non_existent_dataset.csv", "v1.0")
        self.assertFalse(result)

    @patch("scripts.data_versioning.track_dataset")
    @patch("scripts.data_versioning.run_dvc_command")
    @patch("subprocess.run")
    @patch("scripts.data_versioning.tag_dataset_version")
    def test_update_dataset(
        self, mock_tag, mock_subprocess_run, mock_run_cmd, mock_track
    ):
        """Test updating a dataset."""
        # Create a dummy .dvc file
        dvc_file = f"{self.dataset_path}.dvc"
        with open(dvc_file, "w") as f:
            f.write("dummy dvc file")

        # Setup mocks
        mock_run_cmd.return_value = True
        mock_subprocess_run.return_value.returncode = 0
        mock_tag.return_value = True

        # Test successful update with tag
        result = update_dataset(self.dataset_path, "v1.1", "Update dataset")
        self.assertTrue(result)
        mock_run_cmd.assert_called_once_with(
            ["add", "--force", self.dataset_path]
        )
        mock_tag.assert_called_once()

        # Test with non-existent DVC file (should call track_dataset)
        mock_run_cmd.reset_mock()
        mock_track.return_value = True
        os.remove(dvc_file)
        result = update_dataset(self.dataset_path, message="Initial tracking")
        self.assertTrue(result)
        mock_track.assert_called_once_with(
            self.dataset_path, "Initial tracking"
        )

    @patch("scripts.data_versioning.run_dvc_command")
    def test_pull_dataset(self, mock_run_cmd):
        """Test pulling a dataset from remote."""
        # Test pulling all datasets
        mock_run_cmd.return_value = True
        result = pull_dataset()
        self.assertTrue(result)
        mock_run_cmd.assert_called_once_with(["pull"])

        # Test pulling a specific dataset
        mock_run_cmd.reset_mock()
        result = pull_dataset(self.dataset_path)
        self.assertTrue(result)
        mock_run_cmd.assert_called_once_with(["pull", self.dataset_path])

    @patch("yaml.dump")
    def test_create_pipeline(self, mock_yaml_dump):
        """Test creating a DVC pipeline."""
        # Define stages for the pipeline
        stages = [
            {
                "name": "process_data",
                "cmd": "python -m src.data.process",
                "deps": ["data/raw"],
                "outs": ["data/processed"],
            },
            {
                "name": "train_model",
                "cmd": "python -m src.models.train",
                "deps": ["data/processed"],
                "outs": ["models/model.pkl"],
                "metrics": ["metrics/metrics.json"],
            },
        ]

        # Test creating a pipeline
        result = create_pipeline("ml_pipeline", stages)
        self.assertTrue(result)
        mock_yaml_dump.assert_called_once()

        # Verify the file was created with correct structure
        self.assertTrue(os.path.exists("dvc.yaml"))


if __name__ == "__main__":
    unittest.main()
