#!/usr/bin/env python
"""
Kubernetes Deployment Helper

This script helps deploy the ML application to Kubernetes.
It checks for required files, validates configurations, and applies Kubernetes manifests.
"""

import argparse
import logging
import os
import subprocess
import sys
from typing import List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_command(cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
    """
    Run a shell command and return the exit code, stdout, and stderr.
    
    Args:
        cmd: Command to run as a list of strings
        check: Whether to raise an exception if the command fails
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0 and check:
            logger.error(f"Command failed with exit code {process.returncode}")
            logger.error(f"stderr: {stderr}")
            raise subprocess.CalledProcessError(process.returncode, cmd, output=stdout, stderr=stderr)
        
        return process.returncode, stdout, stderr
    
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        if check:
            raise
        return 1, "", str(e)


def check_kubernetes_connection() -> bool:
    """
    Check if kubectl can connect to a Kubernetes cluster.
    
    Returns:
        True if connected, False otherwise
    """
    try:
        exitcode, stdout, stderr = run_command(["kubectl", "cluster-info"], check=False)
        return exitcode == 0
    except:
        return False


def check_required_files() -> bool:
    """
    Check if all required Kubernetes manifests exist.
    
    Returns:
        True if all files exist, False otherwise
    """
    required_files = [
        "k8s/deployment.yaml",
        "k8s/service.yaml",
        "k8s/configmap.yaml",
        "k8s/mlflow-deployment.yaml",
        "k8s/mlflow-service.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    logger.info("All required Kubernetes manifest files found")
    return True


def create_namespace(namespace: str) -> bool:
    """
    Create a Kubernetes namespace if it doesn't exist.
    
    Args:
        namespace: Name of the namespace to create
        
    Returns:
        True if namespace exists or was created, False otherwise
    """
    try:
        # Check if namespace exists
        exitcode, stdout, stderr = run_command(
            ["kubectl", "get", "namespace", namespace], 
            check=False
        )
        
        if exitcode == 0:
            logger.info(f"Namespace {namespace} already exists")
            return True
        
        # Create namespace
        exitcode, stdout, stderr = run_command(
            ["kubectl", "create", "namespace", namespace]
        )
        
        logger.info(f"Created namespace {namespace}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating namespace {namespace}: {str(e)}")
        return False


def apply_kubernetes_manifests(namespace: str, files: Optional[List[str]] = None) -> bool:
    """
    Apply Kubernetes manifests to the cluster.
    
    Args:
        namespace: Namespace to deploy to
        files: List of files to apply (all yaml files in k8s/ by default)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if files is None:
            # Get all YAML files in the k8s directory
            files = [os.path.join("k8s", f) for f in os.listdir("k8s") if f.endswith((".yaml", ".yml"))]
        
        for file_path in files:
            logger.info(f"Applying {file_path}")
            exitcode, stdout, stderr = run_command(
                ["kubectl", "apply", "-f", file_path, "-n", namespace]
            )
            logger.info(f"Applied {file_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error applying Kubernetes manifests: {str(e)}")
        return False


def check_deployment_status(namespace: str, deployment: str, timeout: int = 300) -> bool:
    """
    Check if a deployment is ready.
    
    Args:
        namespace: Namespace of the deployment
        deployment: Name of the deployment
        timeout: Timeout in seconds
        
    Returns:
        True if deployment is ready, False otherwise
    """
    import time
    
    logger.info(f"Waiting for deployment {deployment} to be ready (timeout: {timeout}s)")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            exitcode, stdout, stderr = run_command(
                ["kubectl", "rollout", "status", "deployment", deployment, "-n", namespace],
                check=False
            )
            
            if exitcode == 0 and "successfully rolled out" in stdout:
                logger.info(f"Deployment {deployment} is ready")
                return True
            
            logger.info(f"Waiting for deployment {deployment} to be ready...")
            time.sleep(5)
        
        except Exception as e:
            logger.error(f"Error checking deployment status: {str(e)}")
            time.sleep(5)
    
    logger.error(f"Deployment {deployment} not ready after {timeout} seconds")
    return False


def main():
    """Main function to deploy to Kubernetes."""
    parser = argparse.ArgumentParser(description="Deploy to Kubernetes")
    parser.add_argument("--namespace", type=str, default="mlops",
                      help="Kubernetes namespace to deploy to")
    parser.add_argument("--check-only", action="store_true",
                      help="Only check requirements without deploying")
    parser.add_argument("--files", nargs="+", type=str,
                      help="Specific manifest files to apply")
    
    args = parser.parse_args()
    
    # Step 1: Check connection to Kubernetes
    logger.info("Checking connection to Kubernetes cluster")
    if not check_kubernetes_connection():
        logger.error("Cannot connect to Kubernetes cluster")
        return 1
    
    # Step 2: Check required files
    logger.info("Checking required Kubernetes manifest files")
    if not check_required_files():
        logger.error("Missing required Kubernetes manifest files")
        return 1
    
    if args.check_only:
        logger.info("Check-only mode: All requirements satisfied")
        return 0
    
    # Step 3: Create namespace
    logger.info(f"Creating namespace {args.namespace}")
    if not create_namespace(args.namespace):
        logger.error(f"Failed to create namespace {args.namespace}")
        return 1
    
    # Step 4: Apply manifests
    logger.info("Applying Kubernetes manifests")
    if not apply_kubernetes_manifests(args.namespace, args.files):
        logger.error("Failed to apply Kubernetes manifests")
        return 1
    
    # Step 5: Check deployment status
    deployments = ["mlops-app", "mlflow"]
    for deployment in deployments:
        if not check_deployment_status(args.namespace, deployment):
            logger.error(f"Deployment {deployment} is not ready")
            return 1
    
    logger.info("Deployment completed successfully")
    
    # Print access information
    logger.info("\nAccess Information:")
    logger.info("-----------------")
    
    # Get service information
    exitcode, stdout, stderr = run_command(
        ["kubectl", "get", "service", "-n", args.namespace],
        check=False
    )
    
    if exitcode == 0:
        logger.info(f"Services:\n{stdout}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 