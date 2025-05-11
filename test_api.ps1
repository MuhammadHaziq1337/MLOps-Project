# Test the health endpoint
Write-Host "Testing health endpoint..."
try {
    $health = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
    Write-Host "Health status: $($health.status)"
    Write-Host "Message: $($health.message)"
} catch {
    Write-Host "Error accessing health endpoint: $_"
}

# Test model info endpoint
Write-Host "`nTesting model info endpoint..."
try {
    $info = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/model/info"
    Write-Host "Model type: $($info.model_type)"
    Write-Host "Model path: $($info.model_path)"
} catch {
    Write-Host "Error accessing model info endpoint: $_"
}

# Test prediction endpoint
Write-Host "`nTesting prediction endpoint..."
try {
    # Create request body for Iris dataset (setosa)
    $setosaData = @{
        features = @{
            "sepal length (cm)" = 5.1
            "sepal width (cm)" = 3.5
            "petal length (cm)" = 1.4
            "petal width (cm)" = 0.2
        }
    } | ConvertTo-Json
    
    $prediction = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/predict" -Body $setosaData -ContentType "application/json"
    Write-Host "Prediction result: $($prediction.prediction)"
    
    if ($prediction.confidence) {
        Write-Host "Confidence scores:"
        foreach ($key in $prediction.confidence.PSObject.Properties.Name) {
            Write-Host "  Class $key : $($prediction.confidence.$key)"
        }
    }
    
    if ($prediction.probability) {
        Write-Host "Probability: $($prediction.probability)"
    }
} catch {
    Write-Host "Error accessing prediction endpoint: $_"
}

Write-Host "`nAPI testing completed." 