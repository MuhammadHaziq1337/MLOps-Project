"""
Unit tests for Docker configurations related to monitoring.
"""

import os
import re
import unittest


class TestDockerMonitoring(unittest.TestCase):
    """Tests for Docker configurations related to monitoring."""

    def test_dockerfile_exposes_metrics(self):
        """Test that the Dockerfile exposes the metrics port."""
        dockerfile_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "Dockerfile"
        )

        if not os.path.exists(dockerfile_path):
            self.skipTest("Dockerfile not found")

        with open(dockerfile_path, "r") as f:
            dockerfile_content = f.read()

        # Check for EXPOSE directive for the application port (usually 8000)
        self.assertTrue(
            re.search(r"EXPOSE\s+\d+", dockerfile_content, re.IGNORECASE),
            "Dockerfile does not expose any ports",
        )

    def test_prometheus_client_in_requirements(self):
        """Test that prometheus-client is included in requirements.txt."""
        requirements_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "requirements.txt"
        )

        if not os.path.exists(requirements_path):
            self.skipTest("requirements.txt not found")

        with open(requirements_path, "r") as f:
            requirements_content = f.read()

        # Check that prometheus-client is in requirements.txt
        self.assertTrue(
            re.search(r"prometheus-client", requirements_content),
            "prometheus-client not found in requirements.txt",
        )

    def test_metrics_path_in_app(self):
        """Test that the metrics endpoint is defined in the FastAPI app."""
        app_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "src", "app", "main.py"
        )

        if not os.path.exists(app_path):
            self.skipTest("FastAPI app main.py not found")

        with open(app_path, "r") as f:
            app_content = f.read()

        # Check for metrics endpoint in FastAPI app - use a more flexible
# pattern
        metrics_endpoint_defined = (
            re.search(r'@app\s*\.\s*get\s*\(\s*[\'"]\/metrics', app_content)
            or re.search(r'app\.get\s*\(\s*[\'"]\/metrics', app_content)
            or re.search(r"\/metrics.*PlainTextResponse", app_content)
        )

        self.assertTrue(
            metrics_endpoint_defined,
            "Metrics endpoint not defined in FastAPI app",
        )

        # Check for metrics middleware
        self.assertTrue(
            re.search(r"class\s+MetricsMiddleware", app_content),
            "MetricsMiddleware class not found in FastAPI app",
        )

        # Check middleware is added to the app
        self.assertTrue(
            re.search(
                r"app\s*\.\s*add_middleware\s*\(\s*MetricsMiddleware",
                app_content,
            ),
            "MetricsMiddleware not added to FastAPI app",
        )


if __name__ == "__main__":
    unittest.main()
