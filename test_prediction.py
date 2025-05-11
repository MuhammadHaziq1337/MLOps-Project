import requests

# Define the API endpoint
url = "http://localhost:8000/predict"

# Define the input data - a sample from the Iris dataset (Setosa)
data = {
    "features": {
        "sepal length (cm)": 5.1,
        "sepal width (cm)": 3.5,
        "petal length (cm)": 1.4,
        "petal width (cm)": 0.2
    }
}

print(f"Sending prediction request for data: {data}")

# Make the POST request
try:
    response = requests.post(url, json=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction successful!")
        print(f"Prediction: {result['prediction']}")
        
        # Print confidence scores if available
        if 'confidence' in result:
            print("Confidence scores:")
            for class_id, score in result['confidence'].items():
                print(f"  Class {class_id}: {score:.4f}")
        
        # Print probability if available
        if 'probability' in result and result['probability'] is not None:
            print(f"Probability: {result['probability']:.4f}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"An error occurred: {e}")

print("\nAPI testing completed.") 