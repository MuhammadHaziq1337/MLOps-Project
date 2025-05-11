#!/usr/bin/env python
"""
Data Versioning Script

This script provides utilities for versioning datasets using DVC.
It allows tracking, adding, and versioning datasets with proper tagging.
"""

import argparse
import logging
import os
import subprocess
import sys
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_dvc_command(cmd: List[str], check: bool = True) -> bool:
    """
    Run a DVC command and return whether it was successful.
    
    Args:
        cmd: DVC command to run as a list of strings
        check: Whether to raise an exception if the command fails
        
    Returns:
        True if successful, False otherwise
    """
    full_cmd = ["dvc"] + cmd
    logger.info(f"Running command: {' '.join(full_cmd)}")
    
    try:
        result = subprocess.run(
            full_cmd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.stdout:
            logger.info(result.stdout)
        
        if result.returncode != 0:
            logger.error(f"Command failed with exit code {result.returncode}")
            logger.error(result.stderr)
            return False
        
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {str(e)}")
        logger.error(e.stderr)
        return False
    
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False


def init_dvc(force: bool = False) -> bool:
    """
    Initialize DVC in the project if not already initialized.
    
    Args:
        force: Whether to force initialization even if already initialized
        
    Returns:
        True if successful, False otherwise
    """
    if os.path.exists(".dvc") and not force:
        logger.info("DVC already initialized")
        return True
    
    return run_dvc_command(["init"])


def track_dataset(dataset_path: str, message: Optional[str] = None) -> bool:
    """
    Track a dataset with DVC.
    
    Args:
        dataset_path: Path to the dataset to track
        message: Optional message for the Git commit
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset path does not exist: {dataset_path}")
        return False
    
    # Add dataset to DVC
    if not run_dvc_command(["add", dataset_path]):
        return False
    
    # Add the DVC file to Git
    try:
        dvc_file = f"{dataset_path}.dvc"
        if os.path.exists(dvc_file):
            subprocess.run(["git", "add", dvc_file], check=True)
            
            # Commit the change if a message is provided
            if message:
                subprocess.run(["git", "commit", "-m", message], check=True)
                logger.info(f"Committed DVC file with message: {message}")
            
            logger.info(f"Added dataset {dataset_path} to DVC and Git")
            return True
        else:
            logger.error(f"DVC file not found after adding dataset: {dvc_file}")
            return False
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {str(e)}")
        return False


def tag_dataset_version(dataset_path: str, tag: str, 
                        message: Optional[str] = None) -> bool:
    """
    Tag a dataset version.
    
    Args:
        dataset_path: Path to the dataset
        tag: Tag to apply to the dataset version
        message: Optional message for the tag
        
    Returns:
        True if successful, False otherwise
    """
    dvc_file = f"{dataset_path}.dvc"
    if not os.path.exists(dvc_file):
        logger.error(f"DVC file not found: {dvc_file}")
        return False
    
    # Add a tag using DVC
    tag_cmd = ["tag", "add", "-d", dataset_path, tag]
    if message:
        tag_cmd.extend(["-m", message])
    
    return run_dvc_command(tag_cmd)


def update_dataset(dataset_path: str, tag: Optional[str] = None, message: Optional[str] = None) -> bool:
    """
    Update a tracked dataset and optionally tag the new version.
    
    Args:
        dataset_path: Path to the dataset
        tag: Optional tag to apply to the new version
        message: Optional message for the Git commit
        
    Returns:
        True if successful, False otherwise
    """
    dvc_file = f"{dataset_path}.dvc"
    if not os.path.exists(dvc_file):
        logger.info(f"Dataset not previously tracked, adding it: {dataset_path}")
        return track_dataset(dataset_path, message)
    
    # Update the dataset in DVC
    if not run_dvc_command(["add", "--force", dataset_path]):
        return False
    
    # Add the updated DVC file to Git
    try:
        subprocess.run(["git", "add", dvc_file], check=True)
        
        # Commit the change if a message is provided
        if message:
            subprocess.run(["git", "commit", "-m", message], check=True)
            logger.info(f"Committed updated DVC file with message: {message}")
        
        logger.info(f"Updated dataset {dataset_path} in DVC and Git")
        
        # Tag the new version if a tag is provided
        if tag:
            tag_message = message or f"Tag {tag} for dataset {dataset_path}"
            return tag_dataset_version(dataset_path, tag, tag_message)
        
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {str(e)}")
        return False


def pull_dataset(dataset_path: Optional[str] = None) -> bool:
    """
    Pull dataset(s) from remote storage.
    
    Args:
        dataset_path: Optional path to a specific dataset to pull
        
    Returns:
        True if successful, False otherwise
    """
    cmd = ["pull"]
    if dataset_path:
        cmd.append(dataset_path)
    
    return run_dvc_command(cmd)


def create_pipeline(pipeline_name: str, stages: List[dict]) -> bool:
    """
    Create a DVC pipeline.
    
    Args:
        pipeline_name: Name of the pipeline
        stages: List of stage dictionaries with cmd, deps, and outs
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import yaml

        # Create dvc.yaml file
        dvc_yaml = {
            "stages": {}
        }
        
        for i, stage in enumerate(stages):
            stage_name = stage.get("name", f"{pipeline_name}_stage_{i+1}")
            dvc_yaml["stages"][stage_name] = {
                "cmd": stage["cmd"],
                "deps": stage.get("deps", []),
                "outs": stage.get("outs", [])
            }
            
            # Add parameters if present
            if "params" in stage:
                dvc_yaml["stages"][stage_name]["params"] = stage["params"]
            
            # Add metrics if present
            if "metrics" in stage:
                dvc_yaml["stages"][stage_name]["metrics"] = stage["metrics"]
        
        # Write the YAML file
        with open("dvc.yaml", "w") as f:
            yaml.dump(dvc_yaml, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Created DVC pipeline: {pipeline_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating DVC pipeline: {str(e)}")
        return False


def run_pipeline() -> bool:
    """
    Run the DVC pipeline defined in dvc.yaml.
    
    Returns:
        True if successful, False otherwise
    """
    return run_dvc_command(["repro"])


def main():
    """Parse command line arguments and run DVC operations."""
    parser = argparse.ArgumentParser(description="Data Versioning with DVC")
    
    # Create subparsers for different operations
    subparsers = parser.add_subparsers(dest="operation", help="Operation to perform")
    
    # Initialize DVC
    init_parser = subparsers.add_parser("init", help="Initialize DVC")
    init_parser.add_argument("--force", action="store_true", help="Force initialization")
    
    # Track dataset
    track_parser = subparsers.add_parser("track", help="Track a dataset with DVC")
    track_parser.add_argument("dataset_path", help="Path to the dataset to track")
    track_parser.add_argument("--message", "-m", help="Git commit message")
    
    # Tag dataset version
    tag_parser = subparsers.add_parser("tag", help="Tag a dataset version")
    tag_parser.add_argument("dataset_path", help="Path to the dataset")
    tag_parser.add_argument("tag", help="Tag to apply to the dataset version")
    tag_parser.add_argument("--message", "-m", help="Tag message")
    
    # Update dataset
    update_parser = subparsers.add_parser("update", help="Update a tracked dataset")
    update_parser.add_argument("dataset_path", help="Path to the dataset")
    update_parser.add_argument("--tag", help="Tag to apply to the new version")
    update_parser.add_argument("--message", "-m", help="Git commit message")
    
    # Pull dataset
    pull_parser = subparsers.add_parser("pull", help="Pull dataset(s) from remote storage")
    pull_parser.add_argument("--dataset", help="Path to a specific dataset to pull")
    
    # Run pipeline
    run_parser = subparsers.add_parser("run", help="Run the DVC pipeline")
    
    args = parser.parse_args()
    
    # Execute the requested operation
    if args.operation == "init":
        success = init_dvc(args.force)
    
    elif args.operation == "track":
        success = track_dataset(args.dataset_path, args.message)
    
    elif args.operation == "tag":
        success = tag_dataset_version(args.dataset_path, args.tag, args.message)
    
    elif args.operation == "update":
        success = update_dataset(args.dataset_path, args.tag, args.message)
    
    elif args.operation == "pull":
        success = pull_dataset(args.dataset)
    
    elif args.operation == "run":
        success = run_pipeline()
    
    else:
        parser.print_help()
        return 0
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 