#!/bin/bash
set -e

echo "Installing Docker CLI in Jenkins container..."
docker exec -u 0 jenkins sh -c 'apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release'
docker exec -u 0 jenkins sh -c 'mkdir -p /etc/apt/keyrings'
docker exec -u 0 jenkins sh -c 'curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg'
docker exec -u 0 jenkins sh -c 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null'
docker exec -u 0 jenkins sh -c 'apt-get update && apt-get install -y docker-ce-cli'

echo "Installing Jenkins plugins..."
docker exec jenkins sh -c 'jenkins-plugin-cli --plugins docker-workflow:563.vd5d2e5c4007f'

echo "Restarting Jenkins to apply plugin changes..."
docker restart jenkins

echo "Done. Jenkins should now have Docker capabilities."
echo "Access Jenkins at http://localhost:8082"
echo "Username: admin"
echo "Password: admin" 