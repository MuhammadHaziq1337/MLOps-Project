#!/usr/bin/env python
"""
Create a mock model for testing the MLOps pipeline.
"""
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app.mock_model import save_mock_model

if __name__ == "__main__":
    # Save the mock model
    model_path = save_mock_model()
    print(f"Mock model saved to {model_path}") 