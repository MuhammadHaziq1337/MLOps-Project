#!/bin/bash
# Script to set up and run Jenkins for MLOps with monitoring integration

set -e

echo "Setting up Jenkins for MLOps with monitoring..."

# Ensure script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run with sudo: sudo $0"
  exit 1
fi

# Create required directories if they don't exist
KUBECONFIG_DIR=$HOME/.kube
if [ ! -d "$KUBECONFIG_DIR" ]; then
  echo "Creating Kubernetes config directory..."
  mkdir -p $KUBECONFIG_DIR
  chown -R $SUDO_USER:$SUDO_USER $KUBECONFIG_DIR
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed. Please install Docker before continuing."
  exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
  echo "Docker Compose is not installed. Please install Docker Compose before continuing."
  exit 1
fi

# Build and start Jenkins
echo "Building and starting Jenkins containers..."
cd "$(dirname "$0")"
docker-compose build
docker-compose up -d

# Get the initial admin password
echo "Waiting for Jenkins to start..."
sleep 30

# Check if Jenkins is running
if docker ps | grep -q "jenkins-mlops"; then
  echo "Jenkins is now running!"
  
  # Get the initial admin password if wizard is enabled
  if [ -z "$(docker-compose logs jenkins | grep 'Jenkins is fully up and running')" ]; then
    JENKINS_PASSWORD=$(docker-compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
    echo "Initial admin password: $JENKINS_PASSWORD"
  else
    echo "Jenkins setup wizard is disabled. Default credentials are admin/admin"
  fi
  
  echo "Jenkins is available at: http://localhost:8080"
  echo "Follow the instructions in README.md to complete the setup."
else
  echo "Jenkins failed to start. Check the logs with: docker-compose logs jenkins"
fi

# Provide instructions for credential setup
echo ""
echo "Remember to set up these credentials in Jenkins:"
echo "1. dockerhub-credentials: Your DockerHub username and password"
echo "2. github-credentials: Your GitHub username and personal access token"
echo "3. kubernetes-config: Upload your Kubernetes config file"
echo ""
echo "For more information, see the README.md file in this directory." 