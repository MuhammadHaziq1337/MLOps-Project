#!/usr/bin/env python
"""
ML Pipeline Integration Script

This script provides a unified command-line interface to run various stages
of the machine learning pipeline individually or as an end-to-end workflow.
"""

import argparse
import logging
import os
import subprocess
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "ml_pipeline.log"), mode="a")
    ]
)
logger = logging.getLogger(__name__)

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)


def run_data_processing(dataset="iris", raw_data_dir="data/raw", processed_data_dir="data/processed"):
    """Run data processing step."""
    logger.info(f"Running data processing for {dataset} dataset")
    
    try:
        # Run the data processing script
        cmd = [
            "python", "-m", "src.data.process",
            "--dataset", dataset,
            "--raw-data-dir", raw_data_dir,
            "--processed-data-dir", processed_data_dir
        ]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        logger.info("Data processing completed successfully")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Data processing failed: {str(e)}")
        return False


def run_model_training(dataset="iris", model_type="classification", data_dir="data/processed", 
                      model_dir="models", metrics_file="metrics/model_metrics.json", use_mlflow=True):
    """Run model training step."""
    logger.info(f"Running model training for {dataset} dataset")
    
    try:
        # Run the model training script
        cmd = [
            "python", "-m", "src.models.run_training",
            "--dataset", dataset,
            "--model-type", model_type,
            "--data-dir", data_dir,
            "--model-dir", model_dir,
            "--metrics-file", metrics_file
        ]
        
        if use_mlflow:
            cmd.append("--use-mlflow")
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        logger.info("Model training completed successfully")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Model training failed: {str(e)}")
        return False


def start_model_serving():
    """Start the FastAPI model serving application."""
    logger.info("Starting model serving with FastAPI")
    
    try:
        # Run the FastAPI app
        cmd = ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        
        # Give the server a moment to start
        time.sleep(2)
        
        # Check if the server is running
        if process.poll() is None:
            logger.info("Model serving started successfully")
            return process
        else:
            logger.error("Failed to start model serving")
            return None
    
    except Exception as e:
        logger.error(f"Error starting model serving: {str(e)}")
        return None


def run_full_pipeline(dataset="iris", model_type="classification", use_mlflow=True):
    """Run the entire ML pipeline from data processing to model serving."""
    logger.info(f"Running full ML pipeline for {dataset} dataset")
    
    # Step 1: Data Processing
    if not run_data_processing(dataset):
        logger.error("Pipeline failed at data processing step")
        return False
    
    # Step 2: Model Training
    if not run_model_training(dataset, model_type, use_mlflow=use_mlflow):
        logger.error("Pipeline failed at model training step")
        return False
    
    # Step 3: Start Model Serving
    server_process = start_model_serving()
    if server_process is None:
        logger.error("Pipeline failed at model serving step")
        return False
    
    logger.info("Full ML pipeline completed successfully. Model server is running.")
    logger.info("Press Ctrl+C to stop the server and exit.")
    
    try:
        # Keep the server running until interrupted
        server_process.wait()
    except KeyboardInterrupt:
        logger.info("Stopping model server...")
        server_process.terminate()
        server_process.wait()
        logger.info("Model server stopped")
    
    return True


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ML Pipeline Runner")
    
    # Create subparsers for different stages
    subparsers = parser.add_subparsers(dest="stage", help="Pipeline stage to run")
    
    # Data processing parser
    data_parser = subparsers.add_parser("process", help="Run data processing")
    data_parser.add_argument("--dataset", type=str, default="iris", 
                            help="Dataset to use (iris or california_housing)")
    data_parser.add_argument("--raw-data-dir", type=str, default="data/raw", 
                            help="Directory for raw data")
    data_parser.add_argument("--processed-data-dir", type=str, default="data/processed", 
                            help="Directory for processed data")
    
    # Model training parser
    train_parser = subparsers.add_parser("train", help="Run model training")
    train_parser.add_argument("--dataset", type=str, default="iris", 
                             help="Dataset to use (iris or california_housing)")
    train_parser.add_argument("--model-type", type=str, default="classification", 
                             help="Type of model to train (classification or regression)")
    train_parser.add_argument("--data-dir", type=str, default="data/processed", 
                             help="Directory containing processed data")
    train_parser.add_argument("--model-dir", type=str, default="models", 
                             help="Directory to save trained model")
    train_parser.add_argument("--metrics-file", type=str, default="metrics/model_metrics.json", 
                             help="File to save model metrics")
    train_parser.add_argument("--use-mlflow", action="store_true", 
                             help="Whether to use MLflow for tracking")
    
    # Model serving parser
    serve_parser = subparsers.add_parser("serve", help="Start model serving")
    
    # Full pipeline parser
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full ML pipeline")
    pipeline_parser.add_argument("--dataset", type=str, default="iris", 
                               help="Dataset to use (iris or california_housing)")
    pipeline_parser.add_argument("--model-type", type=str, default="classification", 
                               help="Type of model to train (classification or regression)")
    pipeline_parser.add_argument("--use-mlflow", action="store_true", 
                               help="Whether to use MLflow for tracking")
    
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()
    
    # Ensure necessary directories exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("metrics", exist_ok=True)
    
    if args.stage == "process":
        success = run_data_processing(
            dataset=args.dataset,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir
        )
    
    elif args.stage == "train":
        success = run_model_training(
            dataset=args.dataset,
            model_type=args.model_type,
            data_dir=args.data_dir,
            model_dir=args.model_dir,
            metrics_file=args.metrics_file,
            use_mlflow=args.use_mlflow
        )
    
    elif args.stage == "serve":
        server_process = start_model_serving()
        if server_process:
            try:
                server_process.wait()
                success = True
            except KeyboardInterrupt:
                logger.info("Stopping model server...")
                server_process.terminate()
                server_process.wait()
                logger.info("Model server stopped")
                success = True
        else:
            success = False
    
    elif args.stage == "pipeline":
        success = run_full_pipeline(
            dataset=args.dataset,
            model_type=args.model_type,
            use_mlflow=args.use_mlflow
        )
    
    else:
        parser = argparse.ArgumentParser()
        parser.print_help()
        return 0
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 