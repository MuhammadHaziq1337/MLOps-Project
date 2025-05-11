#!/usr/bin/env python
"""
DVC Data Management Utilities

This script provides utilities for managing data versions with DVC.
It demonstrates how to programmatically work with DVC for data versioning.
"""

import argparse
import logging
import os
import subprocess
import sys
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_command(command: List[str]) -> str:
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {' '.join(command)}")
        logger.error(f"Error message: {e.stderr}")
        return e.stderr

def add_data_file(file_path: str) -> bool:
    """
    Add a data file to DVC tracking.
    
    Args:
        file_path: Path to the data file to add
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Adding file to DVC: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
    
    result = run_command(["dvc", "add", file_path])
    
    if "to track the changes with git" in result.lower():
        dvc_file = f"{file_path}.dvc"
        logger.info(f"File added successfully. DVC file created: {dvc_file}")
        logger.info(f"Don't forget to add the DVC file to git: git add {dvc_file}")
        return True
    else:
        logger.error("Failed to add file to DVC")
        return False

def get_metrics() -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Get the current metrics from DVC.
    
    Returns:
        Dictionary of metrics
    """
    logger.info("Getting metrics from DVC")
    
    try:
        result = run_command(["dvc", "metrics", "show", "--json"])
        import json
        return json.loads(result)
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {}

def run_pipeline(stages: Optional[List[str]] = None) -> bool:
    """
    Run the DVC pipeline.
    
    Args:
        stages: Optional list of specific stages to run
        
    Returns:
        True if successful, False otherwise
    """
    command = ["dvc", "repro"]
    
    if stages:
        command.extend(stages)
    
    logger.info(f"Running DVC pipeline: {' '.join(command)}")
    
    result = run_command(command)
    
    if "failed" in result.lower():
        logger.error("Pipeline execution failed")
        return False
    else:
        logger.info("Pipeline executed successfully")
        return True

def push_data() -> bool:
    """
    Push data to the remote storage.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Pushing data to remote storage")
    
    result = run_command(["dvc", "push"])
    
    if "failed" in result.lower():
        logger.error("Failed to push data to remote storage")
        return False
    else:
        logger.info("Data pushed to remote storage successfully")
        return True

def pull_data() -> bool:
    """
    Pull data from the remote storage.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Pulling data from remote storage")
    
    result = run_command(["dvc", "pull"])
    
    if "failed" in result.lower():
        logger.error("Failed to pull data from remote storage")
        return False
    else:
        logger.info("Data pulled from remote storage successfully")
        return True

def modify_dataset(dataset_path: str, operation: str) -> bool:
    """
    Modify a dataset for testing version control.
    
    Args:
        dataset_path: Path to the dataset to modify
        operation: Type of modification to perform (sample, shuffle, add_noise)
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Modifying dataset: {dataset_path} with operation: {operation}")
    
    try:
        import numpy as np
        import pandas as pd

        # Read the dataset
        df = pd.read_csv(dataset_path)
        original_shape = df.shape
        
        # Apply the requested operation
        if operation == "sample":
            # Take a 80% sample
            df = df.sample(frac=0.8, random_state=42)
        elif operation == "shuffle":
            # Shuffle the dataset
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        elif operation == "add_noise":
            # Add small random noise to numeric columns
            for col in df.select_dtypes(include=[np.number]).columns:
                df[col] = df[col] + np.random.normal(0, df[col].std() * 0.05, size=len(df))
        else:
            logger.error(f"Unknown operation: {operation}")
            return False
        
        # Save the modified dataset
        df.to_csv(dataset_path, index=False)
        logger.info(f"Dataset modified: Original shape {original_shape}, New shape {df.shape}")
        return True
    
    except Exception as e:
        logger.error(f"Error modifying dataset: {e}")
        return False

def main():
    """Main function to parse arguments and perform operations."""
    parser = argparse.ArgumentParser(description="DVC Data Management Utilities")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add file command
    add_parser = subparsers.add_parser("add", help="Add a file to DVC tracking")
    add_parser.add_argument("file_path", help="Path to the file to add")
    
    # Get metrics command
    subparsers.add_parser("metrics", help="Get current metrics from DVC")
    
    # Run pipeline command
    repro_parser = subparsers.add_parser("repro", help="Run the DVC pipeline")
    repro_parser.add_argument("--stages", nargs="+", help="Specific stages to run")
    
    # Push data command
    subparsers.add_parser("push", help="Push data to remote storage")
    
    # Pull data command
    subparsers.add_parser("pull", help="Pull data from remote storage")
    
    # Modify dataset command
    modify_parser = subparsers.add_parser("modify", help="Modify a dataset for testing version control")
    modify_parser.add_argument("dataset_path", help="Path to the dataset to modify")
    modify_parser.add_argument(
        "--operation", 
        choices=["sample", "shuffle", "add_noise"], 
        default="sample",
        help="Type of modification to perform"
    )
    
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "add":
        success = add_data_file(args.file_path)
    elif args.command == "metrics":
        metrics = get_metrics()
        import json
        print(json.dumps(metrics, indent=2))
        success = True
    elif args.command == "repro":
        success = run_pipeline(args.stages)
    elif args.command == "push":
        success = push_data()
    elif args.command == "pull":
        success = pull_data()
    elif args.command == "modify":
        success = modify_dataset(args.dataset_path, args.operation)
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 