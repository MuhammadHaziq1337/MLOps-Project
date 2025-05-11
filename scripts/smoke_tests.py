#!/usr/bin/env python
"""
Smoke tests for the MLOps API deployment.
Runs basic health and functionality checks to verify the deployment.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Union

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("smoke-tests")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run smoke tests against deployed API")
    parser.add_argument(
        "--api-url",
        type=str,
        default=os.environ.get("API_URL", "http://localhost:8000"),
        help="URL of the API to test",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=5,
        help="Number of retries for API calls",
    )
    parser.add_argument(
        "--retry-delay",
        type=int,
        default=5,
        help="Delay between retries in seconds",
    )
    return parser.parse_args()


def make_request(
    url: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    retries: int = 5,
    retry_delay: int = 5,
) -> requests.Response:
    """Make HTTP request with retry logic."""
    for attempt in range(retries):
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached. Last error: {e}")
                raise


def test_health_endpoint(base_url: str, retries: int, retry_delay: int) -> bool:
    """Test the health endpoint."""
    url = f"{base_url}/health"
    logger.info(f"Testing health endpoint: {url}")
    
    try:
        response = make_request(url, retries=retries, retry_delay=retry_delay)
        result = response.json()
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert "status" in result, "Response missing 'status' field"
        assert result["status"] == "healthy", f"Expected status 'healthy', got {result['status']}"
        
        logger.info("Health check passed ✅")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


def test_prediction_endpoint(base_url: str, retries: int, retry_delay: int) -> bool:
    """Test the prediction endpoint with sample data."""
    url = f"{base_url}/predict"
    logger.info(f"Testing prediction endpoint: {url}")
    
    # Sample data for iris dataset prediction
    sample_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    
    try:
        response = make_request(
            url, 
            method="POST", 
            data=sample_data,
            retries=retries,
            retry_delay=retry_delay
        )
        result = response.json()
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert "prediction" in result, "Response missing 'prediction' field"
        
        logger.info("Prediction test passed ✅")
        logger.info(f"Prediction result: {result}")
        return True
    except Exception as e:
        logger.error(f"Prediction test failed: {e}")
        return False


def run_all_tests(api_url: str, retries: int, retry_delay: int) -> bool:
    """Run all smoke tests."""
    logger.info(f"Running smoke tests against {api_url}")
    
    tests = [
        ("Health Check", lambda: test_health_endpoint(api_url, retries, retry_delay)),
        ("Prediction", lambda: test_prediction_endpoint(api_url, retries, retry_delay))
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        result = test_func()
        results.append(result)
        logger.info(f"Test '{test_name}': {'PASSED' if result else 'FAILED'}")
    
    all_passed = all(results)
    logger.info(f"Smoke tests {'PASSED' if all_passed else 'FAILED'}")
    return all_passed


def main() -> int:
    """Entry point for the smoke tests."""
    args = parse_args()
    try:
        success = run_all_tests(args.api_url, args.retries, args.retry_delay)
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Error running smoke tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 