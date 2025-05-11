#!/usr/bin/env python
"""
Test script for the Model API

This script tests the FastAPI model serving endpoint with sample data.
"""

import argparse
import json
import logging
import sys
import time
from typing import Dict, List

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample test data for different datasets
TEST_DATA = {
    'iris': [
        {"features": {"sepal length (cm)": 5.1, "sepal width (cm)": 3.5, "petal length (cm)": 1.4, "petal width (cm)": 0.2}},
        {"features": {"sepal length (cm)": 6.3, "sepal width (cm)": 3.3, "petal length (cm)": 6.0, "petal width (cm)": 2.5}},
        {"features": {"sepal length (cm)": 5.8, "sepal width (cm)": 2.7, "petal length (cm)": 5.1, "petal width (cm)": 1.9}}
    ],
    'california_housing': [
        {"features": {"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984127, "AveBedrms": 1.023810, "Population": 322.0, "AveOccup": 2.555556, "Latitude": 37.88, "Longitude": -122.23}},
        {"features": {"MedInc": 3.2723, "HouseAge": 52.0, "AveRooms": 5.817352, "AveBedrms": 1.073171, "Population": 1467.0, "AveOccup": 3.082437, "Latitude": 34.09, "Longitude": -118.37}},
        {"features": {"MedInc": 5.6431, "HouseAge": 32.0, "AveRooms": 6.216667, "AveBedrms": 0.9750000, "Population": 1387.0, "AveOccup": 2.891667, "Latitude": 33.73, "Longitude": -118.31}}
    ]
}


def check_health(api_url: str) -> bool:
    """
    Check if the API is healthy.
    
    Args:
        api_url: Base URL for the API
    
    Returns:
        True if API is healthy, False otherwise
    """
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        response.raise_for_status()
        health_data = response.json()
        
        if health_data.get("status") == "healthy":
            logger.info("API health check: Healthy")
            return True
        else:
            logger.warning(f"API reports unhealthy status: {health_data}")
            return False
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to API: {str(e)}")
        return False


def get_model_info(api_url: str) -> Dict:
    """
    Get information about the model being served.
    
    Args:
        api_url: Base URL for the API
    
    Returns:
        Dictionary with model information
    """
    try:
        response = requests.get(f"{api_url}/model/info", timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting model info: {str(e)}")
        return {}


def test_prediction(api_url: str, dataset: str, num_samples: int = 3) -> List[Dict]:
    """
    Test the prediction endpoint with sample data.
    
    Args:
        api_url: Base URL for the API
        dataset: Dataset to use for test data
        num_samples: Number of test samples to use
    
    Returns:
        List of prediction results
    """
    if dataset not in TEST_DATA:
        logger.error(f"No test data available for dataset: {dataset}")
        return []
    
    test_samples = TEST_DATA[dataset][:num_samples]
    results = []
    
    for i, sample in enumerate(test_samples):
        try:
            logger.info(f"Testing prediction with sample {i+1}/{len(test_samples)}")
            response = requests.post(
                f"{api_url}/predict",
                json=sample,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Prediction result: {json.dumps(result, indent=2)}")
            results.append(result)
            
            # Slight delay between requests
            time.sleep(0.5)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making prediction: {str(e)}")
            if response := getattr(e, 'response', None):
                logger.error(f"Response status: {response.status_code}")
                logger.error(f"Response body: {response.text}")
    
    return results


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the Model API")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000",
                      help="Base URL for the API")
    parser.add_argument("--dataset", type=str, default="iris",
                      help="Dataset to use for test data")
    parser.add_argument("--samples", type=int, default=3,
                      help="Number of test samples to use")
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    
    logger.info(f"Testing API at {args.api_url} with {args.dataset} dataset")
    
    # Check API health
    if not check_health(args.api_url):
        logger.error("API health check failed. Exiting.")
        return 1
    
    # Get model info
    model_info = get_model_info(args.api_url)
    if model_info:
        logger.info(f"Model info: {json.dumps(model_info, indent=2)}")
    
    # Test predictions
    results = test_prediction(args.api_url, args.dataset, args.samples)
    if not results:
        logger.error("No prediction results obtained. Test failed.")
        return 1
    
    logger.info(f"Successfully tested {len(results)} predictions.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 