"""FastAPI application for model serving."""

import logging
import os
from typing import Dict, Optional, Union

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Innovate Analytics MLOps Project",
    description="API for machine learning model prediction",
    version="0.1.0",
)

# Define model path
MODEL_PATH = os.environ.get("MODEL_PATH", "models/latest")

# Initialize model variable
model = None


class PredictionInput(BaseModel):
    """Input schema for prediction endpoint."""

    features: Dict[str, Union[float, int, str]] = Field(
        ..., description="Features for prediction"
    )


class PredictionResult(BaseModel):
    """Output schema for prediction endpoint."""

    prediction: Union[float, int, str] = Field(
        ..., description="Model prediction"
    )
    probability: Optional[float] = Field(
        None, description="Prediction probability"
    )
    confidence: Optional[Dict[str, float]] = Field(
        None,
        description="Confidence scores for each class",
    )


@app.on_event("startup")
async def load_model():
    """Load the model on startup."""
    global model

    try:
        mlflow_tracking_uri = os.environ.get(
            "MLFLOW_TRACKING_URI",
            "http://localhost:5000",
        )
        mlflow.set_tracking_uri(mlflow_tracking_uri)

        model_path = os.environ.get("MODEL_PATH", "models/latest")

        logger.info(f"Loading model from: {model_path}")
        model = mlflow.pyfunc.load_model(model_path)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        model = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if model is None:
        return {"status": "error", "message": "Model not loaded"}
    return {
        "status": "healthy",
        "message": "Model is loaded and ready for inference",
    }


@app.post("/predict", response_model=PredictionResult)
async def predict(input_data: PredictionInput):
    """Make predictions with the loaded model."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        features_df = pd.DataFrame([input_data.features])
        prediction = model.predict(features_df)
        result = {"prediction": prediction[0]}

        if hasattr(model, "predict_proba"):
            try:
                probabilities = model.predict_proba(features_df)
                if probabilities.shape[1] == 2:
                    result["probability"] = float(probabilities[0][1])
                else:
                    result["confidence"] = {
                        str(i): float(p)
                        for i, p in enumerate(probabilities[0])
                    }
            except Exception as e:
                logger.warning(
                    f"Could not get prediction probabilities: {str(e)}"
                )

        return result

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}",
        )


@app.get("/model/info")
async def model_info():
    """Get information about the loaded model."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        model_info = {
            "model_path": os.environ.get("MODEL_PATH", "models/latest"),
            "mlflow_tracking_uri": os.environ.get(
                "MLFLOW_TRACKING_URI",
                "http://localhost:5000",
            ),
        }

        return model_info

    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting model info: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
