# Jenkins Setup for MLOps Project with Monitoring Integration

This document provides instructions for setting up Jenkins to build, test, and deploy our MLOps project with monitoring components (Prometheus and Grafana).

## Prerequisites

- Jenkins server (2.346.x or later)
- Docker installed on the Jenkins server
- Kubernetes access configured for deployment
- Access to DockerHub or other container registry

## Required Jenkins Plugins

Install the following Jenkins plugins:

- Docker Pipeline
- Kubernetes CLI
- Credentials Binding
- Email Extension
- Blue Ocean (optional, for better UI)

## Jenkins Credentials Setup

1. Add the following credentials in Jenkins:

   - **DockerHub Credentials**: ID: `dockerhub-credentials`, Type: Username with password
   - **GitHub Credentials**: ID: `github-credentials`, Type: Username with password
   - **Kubernetes Config**: ID: `kubernetes-config`, Type: Secret file (upload your kubeconfig file)

## Jenkins Pipeline Setup

1. Create a new Pipeline job in Jenkins
2. Configure it to use the SCM option with your Git repository URL
3. Set the script path to `Jenkinsfile`
4. Configure build triggers as needed (e.g., webhook from GitHub)

## Environment Variables

The pipeline uses the following environment variables:

- `REPO_NAME`: DockerHub repository name (defaults to 'innovateanalytics')
- `PROJECT_NAME`: Project name (defaults to 'mlops-project')
- `VERSION`: Build version (defaults to build number)

## Monitoring Components

The Jenkins pipeline includes steps to:

1. Test monitoring configurations
2. Build and push monitoring container images (Prometheus and Grafana)
3. Deploy and verify monitoring components in both test and production environments

## Docker Images

The pipeline builds and pushes the following Docker images:

- `${REPO_NAME}/${PROJECT_NAME}:${VERSION}` - Main application image
- `${REPO_NAME}/${PROJECT_NAME}-mlflow:${VERSION}` - MLflow tracking server
- `${REPO_NAME}/${PROJECT_NAME}-prometheus:${VERSION}` - Prometheus with ML metrics configuration
- `${REPO_NAME}/${PROJECT_NAME}-grafana:${VERSION}` - Grafana with ML dashboards

## Running Jenkins in Docker

To run Jenkins locally in Docker with the required tools:

```bash
docker run -d --name jenkins-mlops \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.kube:/root/.kube \
  --restart unless-stopped \
  jenkins/jenkins:lts-jdk11
```

After starting, install the required plugins and configure the credentials.

## Configuring Webhook Integration

1. In your GitHub repository, go to Settings > Webhooks > Add webhook
2. Set the Payload URL to `http://<jenkins-url>/github-webhook/`
3. Set Content type to `application/json`
4. Select "Just the push event"
5. Save the webhook

## Troubleshooting

### Docker Access Issues

If Jenkins can't access Docker, run:

```bash
sudo usermod -aG docker jenkins
sudo service jenkins restart
```

### Kubernetes Access Issues

Ensure the kubeconfig file is accessible to Jenkins and has the correct permissions:

```bash
chmod 600 ~/.kube/config
sudo chown jenkins:jenkins ~/.kube/config
```

### Monitoring Tests Failures

If monitoring tests fail:

1. Check Prometheus configuration in `monitoring/prometheus/prometheus.yml`
2. Verify Grafana dashboard configuration in `monitoring/grafana/grafana-k8s.yaml`
3. Ensure metrics are properly implemented in the application (`src/app/main.py`)

## How to Test the Pipeline

1. Make a small change to the codebase and push it
2. Check the Jenkins build logs
3. Verify that all stages, including monitoring tests, are passing
4. Check that Docker images are built and pushed correctly
5. Verify that deployments are updated with the new image versions 