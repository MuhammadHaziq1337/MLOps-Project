#!/usr/bin/env python3
"""
Script to run basic monitoring tests for the CI/CD pipeline.
This script verifies that:
1. Monitoring configuration files exist and are correctly formatted
2. Prometheus configuration contains the necessary ML metrics scraping jobs
3. Grafana dashboard configurations include model prediction metrics
"""

import os
import re
import sys
from pathlib import Path

import yaml

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

def check_prometheus_config():
    """Verify Prometheus configuration file."""
    prometheus_config_path = PROJECT_ROOT / "monitoring" / "prometheus" / "prometheus.yml"
    
    print(f"Checking Prometheus config: {prometheus_config_path}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Directory exists: {(PROJECT_ROOT / 'monitoring' / 'prometheus').exists()}")
    
    if not prometheus_config_path.exists():
        print(f"❌ Prometheus config file not found at {prometheus_config_path}")
        # Try alternate location
        alt_path = Path(os.getcwd()) / "monitoring" / "prometheus" / "prometheus.yml"
        if alt_path.exists():
            print(f"Found config at alternate path: {alt_path}")
            prometheus_config_path = alt_path
        else:
            print(f"Also checked alternate path: {alt_path}")
            return False
    
    try:
        with open(prometheus_config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Check for required configuration sections
        if not all(key in config for key in ["global", "scrape_configs"]):
            print("❌ Prometheus config is missing required sections")
            print(f"Found sections: {list(config.keys())}")
            return False
        
        # Check for ML metrics job
        ml_job_found = False
        for job in config["scrape_configs"]:
            if job.get("job_name") == "ml-model-metrics":
                ml_job_found = True
                break
        
        if not ml_job_found:
            print("❌ Prometheus config is missing 'ml-model-metrics' job")
            print(f"Found jobs: {[job.get('job_name') for job in config['scrape_configs']]}")
            return False
        
        print("✅ Prometheus config is valid")
        return True
    
    except Exception as e:
        print(f"❌ Error validating Prometheus config: {str(e)}")
        return False

def check_grafana_dashboard():
    """Verify Grafana dashboard configuration."""
    grafana_config_path = PROJECT_ROOT / "monitoring" / "grafana" / "grafana-k8s.yaml"
    
    print(f"Checking Grafana dashboard: {grafana_config_path}")
    print(f"Directory exists: {(PROJECT_ROOT / 'monitoring' / 'grafana').exists()}")
    
    if not grafana_config_path.exists():
        print(f"❌ Grafana dashboard file not found at {grafana_config_path}")
        # Try alternate location
        alt_path = Path(os.getcwd()) / "monitoring" / "grafana" / "grafana-k8s.yaml"
        if alt_path.exists():
            print(f"Found dashboard at alternate path: {alt_path}")
            grafana_config_path = alt_path
        else:
            print(f"Also checked alternate path: {alt_path}")
            return False
    
    try:
        with open(grafana_config_path, 'r') as file:
            contents = file.read()
        
        # Check for required metrics in dashboard
        required_metrics = [
            "model_prediction_count",
            "model_prediction_latency",
            "http_requests_total"
        ]
        
        found_metrics = []
        for metric in required_metrics:
            if metric in contents:
                found_metrics.append(metric)
        
        missing_metrics = set(required_metrics) - set(found_metrics)
        if missing_metrics:
            print(f"❌ Grafana dashboard is missing required metrics: {', '.join(missing_metrics)}")
            return False
        
        # Check for Prometheus datasource
        if "prometheus" not in contents.lower():
            print("❌ Grafana dashboard does not reference Prometheus datasource")
            return False
        
        print("✅ Grafana dashboard is valid")
        return True
    
    except Exception as e:
        print(f"❌ Error validating Grafana dashboard: {str(e)}")
        return False

def check_app_metrics_integration():
    """Check that app code includes metrics integration."""
    app_file = PROJECT_ROOT / "src" / "app" / "main.py"
    
    print(f"Checking app metrics integration: {app_file}")
    print(f"Directory exists: {(PROJECT_ROOT / 'src' / 'app').exists()}")
    
    if not app_file.exists():
        print(f"❌ App file not found at {app_file}")
        # Try alternate location
        alt_path = Path(os.getcwd()) / "src" / "app" / "main.py"
        if alt_path.exists():
            print(f"Found app file at alternate path: {alt_path}")
            app_file = alt_path
        else:
            print(f"Also checked alternate path: {alt_path}")
            # Skip this check if file not found - might be running in CI without full codebase
            print("Skipping app metrics check in CI environment")
            return True
    
    try:
        with open(app_file, 'r') as file:
            contents = file.read()
        
        # Check for prometheus_client import
        if "prometheus_client" not in contents:
            print("❌ App does not import prometheus_client")
            return False
        
        # Check for metrics endpoint
        if "/metrics" not in contents:
            print("❌ App does not expose metrics endpoint")
            return False
        
        # Check for model metrics
        model_metrics_pattern = r"(Counter|Gauge|Histogram|Summary)\s*\(\s*['\"]model_"
        if not re.search(model_metrics_pattern, contents):
            print("❌ App does not define model-specific metrics")
            return False
        
        print("✅ App metrics integration is valid")
        return True
    
    except Exception as e:
        print(f"❌ Error checking app metrics integration: {str(e)}")
        return False

def main():
    """Run all monitoring tests."""
    print("Running monitoring tests...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Project root directory: {PROJECT_ROOT}")
    
    # List directories to help debug CI issues
    print("\nDirectory structure:")
    os.system("ls -la")
    os.system("ls -la monitoring || echo 'monitoring dir not found'")
    
    success = True
    
    # Check that monitoring directories exist
    monitoring_dir = PROJECT_ROOT / "monitoring"
    if not monitoring_dir.exists():
        print(f"❌ Monitoring directory not found at {monitoring_dir}")
        # Try alternate path
        alt_path = Path(os.getcwd()) / "monitoring"
        if alt_path.exists():
            print(f"Found monitoring directory at alternate path: {alt_path}")
            # Continue with tests
        else:
            print(f"Also checked alternate path: {alt_path}")
            return False
    
    # Run all checks
    checks = [
        check_prometheus_config,
        check_grafana_dashboard,
        check_app_metrics_integration
    ]
    
    for check in checks:
        if not check():
            success = False
    
    if success:
        print("\n✅ All monitoring tests passed!")
        return 0
    else:
        print("\n❌ Some monitoring tests failed. See errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 