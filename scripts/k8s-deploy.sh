#!/bin/bash
set -e

# Default values
ENVIRONMENT="dev"
VERSION="latest"
NAMESPACE="mlops"
KUBE_CONTEXT=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --version)
      VERSION="$2"
      shift 2
      ;;
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    --context)
      KUBE_CONTEXT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set Kubernetes context if provided
if [ -n "$KUBE_CONTEXT" ]; then
  kubectl config use-context "$KUBE_CONTEXT"
fi

echo "Deploying to environment: $ENVIRONMENT"
echo "Using image version: $VERSION"
echo "Using namespace: $NAMESPACE"

# Create namespace if it doesn't exist
kubectl get namespace "$NAMESPACE" || kubectl create -f k8s/namespace.yaml

# Replace the VERSION placeholder in yaml files
find k8s -type f -name "*.yaml" -exec sed -i "s/{{VERSION}}/$VERSION/g" {} \;

# Apply Kubernetes resources
echo "Applying Kubernetes resources..."
kubectl apply -k k8s/

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/mlops-project -n "$NAMESPACE"
kubectl rollout status deployment/mlflow -n "$NAMESPACE"

echo "Deployment completed successfully!" 