"""
Data processing script that downloads and prepares data for model training.
"""

import argparse
import logging
import os

import pandas as pd
from sklearn.datasets import fetch_california_housing, load_iris

from src.data.preprocessing import clean_data, split_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_dataset(dataset_name: str, output_dir: str) -> pd.DataFrame:
    """
    Download or load dataset.

    Args:
        dataset_name: Name of the dataset to download
        output_dir: Directory to save raw data

    Returns:
        Loaded dataset as pandas DataFrame
    """
    os.makedirs(output_dir, exist_ok=True)

    if dataset_name == "iris":
        logger.info("Loading Iris dataset")
        iris = load_iris()
        df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
        df["target"] = iris.target
        path = os.path.join(output_dir, "iris.csv")
        df.to_csv(path, index=False)
        logger.info(f"Saved raw data to {path}")
        return df

    elif dataset_name == "california_housing":
        logger.info("Loading California Housing dataset")
        housing = fetch_california_housing()
        df = pd.DataFrame(data=housing.data, columns=housing.feature_names)
        df["target"] = housing.target
        path = os.path.join(output_dir, "california_housing.csv")
        df.to_csv(path, index=False)
        logger.info(f"Saved raw data to {path}")
        return df

    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


def process_data(df: pd.DataFrame, dataset_name: str, output_dir: str) -> None:
    """
    Process the data and save train/test splits.

    Args:
        df: Input DataFrame to process
        dataset_name: Name of the dataset
        output_dir: Directory to save processed data
    """
    os.makedirs(output_dir, exist_ok=True)

    logger.info("Cleaning data")
    df_clean = clean_data(df)

    logger.info("Splitting data into train/test sets")
    X_train, X_test, y_train, y_test = split_data(
        df_clean, target_col="target", test_size=0.2
    )

    logger.info(f"Saving processed data to {output_dir}")
    X_train.to_csv(
        os.path.join(output_dir, f"{dataset_name}_X_train.csv"),
        index=False
    )
    X_test.to_csv(
        os.path.join(output_dir, f"{dataset_name}_X_test.csv"),
        index=False
    )
    y_train.to_csv(
        os.path.join(output_dir, f"{dataset_name}_y_train.csv"),
        index=False
    )
    y_test.to_csv(
        os.path.join(output_dir, f"{dataset_name}_y_test.csv"),
        index=False
    )

    logger.info("Data processing complete")


def main():
    """Main function to run data processing."""
    parser = argparse.ArgumentParser(description="Process data for ML model")
    parser.add_argument(
        "--dataset",
        type=str,
        default="iris",
        help="Dataset to use (iris or california_housing)",
    )
    parser.add_argument(
        "--raw-data-dir",
        type=str,
        default="data/raw",
        help="Directory for raw data",
    )
    parser.add_argument(
        "--processed-data-dir",
        type=str,
        default="data/processed",
        help="Directory for processed data",
    )

    args = parser.parse_args()

    logger.info(f"Processing {args.dataset} dataset")

    df = get_dataset(args.dataset, args.raw_data_dir)
    process_data(df, args.dataset, args.processed_data_dir)

    logger.info("Data processing pipeline completed successfully")


if __name__ == "__main__":
    main()
