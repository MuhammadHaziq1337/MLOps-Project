# Build the custom Jenkins image
$rootDir = Join-Path $PSScriptRoot ".."
docker build -t jenkins-with-docker -f "$rootDir\Dockerfile.jenkins" "$rootDir"

# Start Jenkins with Docker socket mounted
docker run -d `
  --name jenkins-docker `
  --user root `
  -p 8082:8080 -p 50000:50000 `
  -v jenkins_data:/var/jenkins_home `
  -v "/var/run/docker.sock:/var/run/docker.sock" `
  --restart=unless-stopped `
  jenkins-with-docker

# Print instructions
Write-Host "Custom Jenkins with Docker CLI is starting on http://localhost:8082" -ForegroundColor Green
Write-Host "Retrieve the initial admin password with:" -ForegroundColor Yellow
Write-Host "docker exec jenkins-docker cat /var/jenkins_home/secrets/initialAdminPassword" -ForegroundColor Yellow 