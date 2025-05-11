"""Data preprocessing module for the ML pipeline."""

from typing import Optional, Tuple

import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load dataset from a file.

    Args:
        file_path: Path to the data file

    Returns:
        Loaded data as a pandas DataFrame
    """
    logger.info(f"Loading data from {file_path}")

    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".parquet"):
        return pd.read_parquet(file_path)
    elif file_path.endswith(".json"):
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning data")

    df = df.drop_duplicates()

    for col in df.columns:
        if np.issubdtype(df[col].dtype, np.number):
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(
                df[col].mode()[0] if not df[col].mode().empty else ""
            )

    return df


def split_data(
    df: pd.DataFrame,
    target_col: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into training and test sets.

    Args:
        df: Input DataFrame
        target_col: Target column name
        test_size: Proportion of data to use for test set
        random_state: Random seed for reproducibility

    Returns:
        X_train, X_test, y_train, y_test
    """
    logger.info(f"Splitting data with test_size={test_size}")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    return train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )


def scale_features(
    X_train: pd.DataFrame, X_test: Optional[pd.DataFrame] = None
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], StandardScaler]:
    """
    Scale features using StandardScaler.

    Args:
        X_train: Training data
        X_test: Test data (optional)

    Returns:
        Scaled X_train, scaled X_test (if provided), and the fitted scaler
    """
    logger.info("Scaling features")

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index,
    )

    X_test_scaled = None
    if X_test is not None:
        X_test_scaled = pd.DataFrame(
            scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index,
        )

    return X_train_scaled, X_test_scaled, scaler
