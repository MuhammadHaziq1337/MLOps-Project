"""
Tests for the monitoring components of the MLOps project.
"""

import unittest

import yaml


class TestMonitoringK8s(unittest.TestCase):
    """Test monitoring configurations for Kubernetes deployments."""

    def test_prometheus_config(self):
        """Test that Prometheus configuration file is valid."""
        try:
            # Load the Prometheus configuration file
            with open("monitoring/prometheus/prometheus.yml", "r") as f:
                config = yaml.safe_load(f)

            # Verify basic structure
            self.assertIn("global", config)
            self.assertIn("scrape_interval", config["global"])
            self.assertIn("scrape_configs", config)

            # Check for required job configurations
            job_names = [job["job_name"] for job in config["scrape_configs"]]
            self.assertIn("prometheus", job_names)
            self.assertIn("ml-model-metrics", job_names)

            # Verify ML model metrics job
            ml_job = next(
                job
                for job in config["scrape_configs"]
                if job["job_name"] == "ml-model-metrics"
            )
            self.assertEqual(ml_job["metrics_path"], "/metrics")
            self.assertIn("static_configs", ml_job)
            self.assertTrue(len(ml_job["static_configs"]) > 0)
            self.assertIn("targets", ml_job["static_configs"][0])

        except Exception as e:
            self.fail(f"Failed to validate Prometheus configuration: {str(e)}")

    def test_prometheus_k8s_yaml(self):
        """Test that the Prometheus Kubernetes deployment file is valid."""
        try:
            # Load the Prometheus Kubernetes deployment file
            with open("monitoring/prometheus/prometheus-k8s.yaml", "r") as f:
                # Split YAML document into individual parts (it contains
                # multiple resources)
                docs = list(yaml.safe_load_all(f))

            # Check for required Kubernetes resources
            resource_kinds = [doc.get("kind") for doc in docs if isinstance(doc, dict)]
            self.assertIn("Namespace", resource_kinds)
            self.assertIn("ConfigMap", resource_kinds)
            self.assertIn("Deployment", resource_kinds)
            self.assertIn("Service", resource_kinds)

            # Verify the ConfigMap includes the Prometheus configuration
            config_maps = [doc for doc in docs if doc.get("kind") == "ConfigMap"]
            prometheus_config = None
            for cm in config_maps:
                if cm.get("metadata", {}).get("name") == "prometheus-config":
                    prometheus_config = cm
                    break

            self.assertIsNotNone(prometheus_config, "Prometheus ConfigMap not found")
            self.assertIn("prometheus.yml", prometheus_config.get("data", {}))

            # Verify the Deployment configuration
            deployments = [doc for doc in docs if doc.get("kind") == "Deployment"]
            prometheus_deployment = None
            for dep in deployments:
                if dep.get("metadata", {}).get("name") == "prometheus":
                    prometheus_deployment = dep
                    break

            self.assertIsNotNone(
                prometheus_deployment, "Prometheus Deployment not found"
            )
            container_specs = (
                prometheus_deployment.get("spec", {})
                .get("template", {})
                .get("spec", {})
                .get("containers", [])
            )
            self.assertTrue(
                len(container_specs) > 0,
                "No containers found in Prometheus deployment",
            )

            # Verify prometheus container
            prometheus_container = container_specs[0]
            self.assertEqual(prometheus_container.get("name"), "prometheus")
            self.assertIn("prom/prometheus", prometheus_container.get("image"))

        except Exception as e:
            self.fail(
                f"Failed to validate Prometheus Kubernetes deployment: " f"{str(e)}"
            )

    def test_grafana_k8s_yaml(self):
        """Test that the Grafana Kubernetes deployment file is valid."""
        try:
            # Load the Grafana Kubernetes deployment file
            with open("monitoring/grafana/grafana-k8s.yaml", "r") as f:
                # Split YAML document into individual parts (it contains
                # multiple resources)
                docs = list(yaml.safe_load_all(f))

            # Check for required Kubernetes resources
            resource_kinds = [doc.get("kind") for doc in docs if isinstance(doc, dict)]
            self.assertIn("Deployment", resource_kinds)
            self.assertIn("Service", resource_kinds)
            self.assertIn("ConfigMap", resource_kinds)

            # Verify the Deployment configuration
            deployments = [doc for doc in docs if doc.get("kind") == "Deployment"]
            grafana_deployment = None
            for dep in deployments:
                if dep.get("metadata", {}).get("name") == "grafana":
                    grafana_deployment = dep
                    break

            self.assertIsNotNone(grafana_deployment, "Grafana Deployment not found")
            container_specs = (
                grafana_deployment.get("spec", {})
                .get("template", {})
                .get("spec", {})
                .get("containers", [])
            )
            self.assertTrue(
                len(container_specs) > 0,
                "No containers found in Grafana deployment",
            )

            # Verify grafana container
            grafana_container = container_specs[0]
            self.assertEqual(grafana_container.get("name"), "grafana")
            self.assertIn("grafana/grafana", grafana_container.get("image"))

            # Verify Grafana ConfigMaps
            config_maps = [doc for doc in docs if doc.get("kind") == "ConfigMap"]
            grafana_dashboards_cm = None
            for cm in config_maps:
                if cm.get("metadata", {}).get("name") == "grafana-dashboards":
                    grafana_dashboards_cm = cm
                    break

            self.assertIsNotNone(
                grafana_dashboards_cm, "Grafana dashboards ConfigMap not found"
            )
            self.assertIn(
                "ml-metrics-dashboard.json",
                grafana_dashboards_cm.get("data", {}),
            )

            # Verify the dashboard contains monitoring for ML metrics
            dashboard_json = grafana_dashboards_cm.get("data", {}).get(
                "ml-metrics-dashboard.json"
            )
            self.assertIsNotNone(dashboard_json)
            # Convert from string to dict
            dashboard = yaml.safe_load(dashboard_json)
            self.assertIn("panels", dashboard)

            # Check that we have panels for monitoring ML metrics
            panel_titles = [panel.get("title") for panel in dashboard.get("panels", [])]
            ml_related_titles = [
                title
                for title in panel_titles
                if any(
                    kw in title.lower()
                    for kw in [
                        "api",
                        "prediction",
                        "feature",
                        "model",
                        "request",
                    ]
                )
            ]
            self.assertTrue(
                len(ml_related_titles) > 0,
                "No ML-related panels found in Grafana dashboard",
            )

        except Exception as e:
            self.fail(f"Failed to validate Grafana Kubernetes deployment: {str(e)}")


if __name__ == "__main__":
    unittest.main()
