#!/usr/bin/env python3
"""
Script to test monitoring components in Docker before deploying to Kubernetes.
This script builds and runs Docker containers for the FastAPI app, Prometheus, and Grafana,
then verifies that metrics are being properly collected and displayed.
"""

import argparse
import os
import subprocess
import sys
import time

import requests

# Directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Project root directory
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def run_command(command, check=True):
    """Run a shell command and return the output."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        if check:
            sys.exit(1)
        return e

def build_images():
    """Build Docker images for the application and monitoring components."""
    print("Building Docker images...")
    
    # Build FastAPI app image
    run_command("docker build -t mlops-app:test .")
    
    # Build Prometheus image
    os.chdir(os.path.join(PROJECT_ROOT, "monitoring", "prometheus"))
    run_command("docker build -t mlops-prometheus:test .")
    
    # Build Grafana image
    os.chdir(os.path.join(PROJECT_ROOT, "monitoring", "grafana"))
    run_command("docker build -t mlops-grafana:test .")
    
    # Return to project root
    os.chdir(PROJECT_ROOT)

def start_containers():
    """Start Docker containers for testing monitoring integration."""
    print("Starting Docker containers...")
    
    # Create Docker network
    run_command("docker network create mlops-test-network", check=False)
    
    # Start FastAPI app container
    run_command(
        "docker run -d --name mlops-app-test --network mlops-test-network -p 8000:8000 mlops-app:test"
    )
    
    # Modify Prometheus config to use the container name for the ML app
    with open(os.path.join(PROJECT_ROOT, "monitoring", "prometheus", "prometheus.yml"), "r") as f:
        prometheus_config = f.read()
    
    # Create a temporary file with modified config
    temp_prometheus_config = prometheus_config.replace(
        'targets: ["mlops-app.mlops.svc.cluster.local:8000"]',
        'targets: ["mlops-app-test:8000"]'
    ).replace(
        'targets: ["node-exporter.mlops.svc.cluster.local:9100"]',
        'targets: ["localhost:9100"]'
    )
    
    temp_config_path = os.path.join(PROJECT_ROOT, "monitoring", "prometheus", "prometheus.test.yml")
    with open(temp_config_path, "w") as f:
        f.write(temp_prometheus_config)
    
    # Start Prometheus container with modified config
    run_command(
        f"docker run -d --name mlops-prometheus-test --network mlops-test-network -p 9090:9090 -v {temp_config_path}:/etc/prometheus/prometheus.yml mlops-prometheus:test"
    )
    
    # Start Grafana container
    run_command(
        "docker run -d --name mlops-grafana-test --network mlops-test-network -p 3000:3000 mlops-grafana:test"
    )
    
    # Wait for containers to start
    print("Waiting for containers to start...")
    time.sleep(5)

def verify_monitoring():
    """Verify that monitoring components are working correctly."""
    print("Verifying monitoring setup...")
    
    # Verify FastAPI app is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ FastAPI app is running")
        else:
            print(f"❌ FastAPI app returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to connect to FastAPI app: {str(e)}")
        return False
    
    # Verify metrics endpoint is exposed
    try:
        response = requests.get("http://localhost:8000/metrics")
        if response.status_code == 200:
            print("✅ Metrics endpoint is exposed")
            if "http_requests" in response.text and "model_prediction" in response.text:
                print("✅ Metrics contain expected ML monitoring data")
            else:
                print("❌ Metrics do not contain expected ML monitoring data")
                return False
        else:
            print(f"❌ Metrics endpoint returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to connect to metrics endpoint: {str(e)}")
        return False
    
    # Verify Prometheus is running and can scrape metrics
    try:
        response = requests.get("http://localhost:9090/-/ready")
        if response.status_code == 200:
            print("✅ Prometheus is running")
        else:
            print(f"❌ Prometheus returned status code {response.status_code}")
            return False
        
        # Check that Prometheus is scraping our metrics
        time.sleep(5)  # Wait for Prometheus to scrape metrics
        response = requests.get(
            "http://localhost:9090/api/v1/targets"
        )
        if response.status_code == 200:
            targets = response.json()
            ml_app_found = False
            for target in targets.get("data", {}).get("activeTargets", []):
                if "mlops-app-test" in target.get("labels", {}).get("instance", ""):
                    ml_app_found = True
                    if target.get("health") == "up":
                        print("✅ Prometheus is successfully scraping ML app metrics")
                    else:
                        print("❌ Prometheus is not successfully scraping ML app metrics")
                        return False
            
            if not ml_app_found:
                print("❌ ML app target not found in Prometheus")
                return False
        else:
            print(f"❌ Prometheus API returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to connect to Prometheus: {str(e)}")
        return False
    
    # Verify Grafana is running
    try:
        response = requests.get("http://localhost:3000/api/health")
        if response.status_code == 200:
            print("✅ Grafana is running")
        else:
            print(f"❌ Grafana returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to connect to Grafana: {str(e)}")
        return False
    
    # Generate some test data by making predictions
    print("Generating test data...")
    test_data = {
        "features": {
            "sepal length (cm)": 5.1,
            "sepal width (cm)": 3.5,
            "petal length (cm)": 1.4,
            "petal width (cm)": 0.2
        }
    }
    
    for _ in range(5):
        try:
            response = requests.post("http://localhost:8000/predict", json=test_data)
            if response.status_code == 200:
                print(f"✅ Made test prediction: {response.json()['prediction']}")
            else:
                print(f"❌ Prediction endpoint returned status code {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Failed to make test prediction: {str(e)}")
    
    print("All monitoring components are working correctly!")
    return True

def stop_containers():
    """Stop and remove Docker containers used for testing."""
    print("Stopping Docker containers...")
    
    run_command("docker stop mlops-app-test mlops-prometheus-test mlops-grafana-test", check=False)
    run_command("docker rm mlops-app-test mlops-prometheus-test mlops-grafana-test", check=False)
    run_command("docker network rm mlops-test-network", check=False)
    
    # Remove temporary Prometheus config
    temp_config_path = os.path.join(PROJECT_ROOT, "monitoring", "prometheus", "prometheus.test.yml")
    if os.path.exists(temp_config_path):
        os.remove(temp_config_path)

def main():
    parser = argparse.ArgumentParser(description="Test monitoring integration in Docker")
    parser.add_argument("--skip-build", action="store_true", help="Skip building Docker images")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip cleaning up containers after testing")
    
    args = parser.parse_args()
    
    try:
        if not args.skip_build:
            build_images()
        
        start_containers()
        
        success = verify_monitoring()
        
        if not args.skip_cleanup:
            stop_containers()
        
        if success:
            print("✅ Monitoring test completed successfully")
            return 0
        else:
            print("❌ Monitoring test failed")
            return 1
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        if not args.skip_cleanup:
            stop_containers()
        return 1
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        if not args.skip_cleanup:
            stop_containers()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 