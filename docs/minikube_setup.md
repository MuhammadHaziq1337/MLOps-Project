# Minikube Setup Guide

This guide explains how to set up Minikube for local Kubernetes development in the Innovate Analytics MLOps project.

## Prerequisites

Before setting up Minikube, ensure you have:

- **Docker**: Required for running containers locally
- **kubectl**: Kubernetes command-line tool
- **VirtualBox** or another hypervisor (optional, based on your OS)

## Installation

### Windows

1. **Install Chocolatey** (if not already installed):
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Install Minikube using Chocolatey**:
   ```powershell
   choco install minikube
   ```

3. **Verify installation**:
   ```powershell
   minikube version
   ```

### macOS

1. **Install with Homebrew**:
   ```bash
   brew install minikube
   ```

2. **Verify installation**:
   ```bash
   minikube version
   ```

### Linux (Ubuntu/Debian)

1. **Download and install Minikube**:
   ```bash
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

2. **Verify installation**:
   ```bash
   minikube version
   ```

## Starting Minikube

Start Minikube with the following command:

```bash
minikube start --driver=docker --memory=4g --cpus=2
```

Options explained:
- `--driver=docker`: Use Docker as the virtualization driver
- `--memory=4g`: Allocate 4GB of memory (adjust based on your machine)
- `--cpus=2`: Allocate 2 CPU cores (adjust based on your machine)

To verify Minikube is running:

```bash
minikube status
```

## Using Minikube with kubectl

Once Minikube is started, you can use kubectl to interact with your local Kubernetes cluster.

1. **Check cluster info**:
   ```bash
   kubectl cluster-info
   ```

2. **Check nodes**:
   ```bash
   kubectl get nodes
   ```

3. **List all resources**:
   ```bash
   kubectl get all --all-namespaces
   ```

## Using Minikube Docker Environment

To use the Docker daemon inside Minikube instead of your local Docker:

### On Linux/macOS:

```bash
eval $(minikube docker-env)
```

### On Windows (PowerShell):

```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

After running this command, any Docker build commands will use the Minikube Docker daemon, allowing your Kubernetes cluster to access locally built images without pushing to a registry.

## Deploying Our Application to Minikube

### 1. Deploy using kubectl

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 2. Deploy using our deployment script

Our project provides a Python script for easier deployment:

```bash
python scripts/k8s_deploy.py --namespace mlops
```

### 3. Using Minikube addons

Minikube comes with useful addons that you can enable:

```bash
# Enable dashboard
minikube addons enable dashboard

# Enable metrics-server for HPA
minikube addons enable metrics-server

# List all available addons
minikube addons list
```

## Accessing Deployed Services

### 1. Using minikube service

The easiest way to access a service is:

```bash
minikube service mlops-app -n mlops
```

This will open a browser window with the correct URL.

### 2. Port forwarding

Alternatively, you can use port forwarding:

```bash
kubectl port-forward service/mlops-app 8000:8000 -n mlops
```

Then access the service at http://localhost:8000

### 3. Get service URL

```bash
minikube service mlops-app -n mlops --url
```

## Monitoring the Deployment

Monitor the deployed application:

```bash
# Check pod status
kubectl get pods -n mlops

# View pod logs
kubectl logs deployment/mlops-app -n mlops

# Describe deployment
kubectl describe deployment mlops-app -n mlops
```

## Starting the Dashboard

Minikube includes the Kubernetes Dashboard, which provides a web UI:

```bash
minikube dashboard
```

## Cleaning Up

When you're done, you can:

1. **Delete deployments**:
   ```bash
   kubectl delete -f k8s/
   ```

2. **Stop Minikube**:
   ```bash
   minikube stop
   ```

3. **Delete Minikube cluster**:
   ```bash
   minikube delete
   ```

## Troubleshooting

### Common Issues

1. **ImagePullBackOff error**:
   - Ensure you're using the Minikube Docker daemon 
   - Check image names and tags are correct
   - Verify images exist locally (if not using a registry)

2. **Connection refused errors**:
   - Ensure Minikube is running (`minikube status`)
   - Check service and pod status
   - Verify port mappings are correct

3. **Resource constraints**:
   - Increase memory/CPU allocation if containers are being terminated
   ```bash
   minikube stop
   minikube start --driver=docker --memory=6g --cpus=4
   ```

### Useful Commands

1. **SSH into Minikube node**:
   ```bash
   minikube ssh
   ```

2. **Check Minikube logs**:
   ```bash
   minikube logs
   ```

3. **Reset Minikube cluster**:
   ```bash
   minikube delete
   minikube start --driver=docker
   ```

## Conclusion

Minikube provides a lightweight Kubernetes environment for local development and testing. It allows you to develop and test your Kubernetes deployments without needing a full-scale cluster.

For more information, see the [official Minikube documentation](https://minikube.sigs.k8s.io/docs/). 