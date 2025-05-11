"""
FastAPI application for serving machine learning models.
"""

import logging
import os
import pickle
from typing import Dict, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from src.app import metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ML Model API",
    description="API for serving machine learning models",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = request.url.path
        start_time = metrics.record_request_start(method, path)

        response = await call_next(request)

        metrics.record_request_end(
            start_time, method, path, response.status_code
        )

        return response


# Add metrics middleware
app.add_middleware(MetricsMiddleware)

MODEL_DIR = os.environ.get("MODEL_DIR", "models")
DEFAULT_MODEL = os.environ.get(
    "DEFAULT_MODEL", "iris_classification_model.pkl"
)


class PredictionRequest(BaseModel):
    features: Dict[str, float]
    model_name: Optional[str] = None


class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    model_name: str
    model_version: str


def load_model(model_name: str):
    model_path = os.path.join(MODEL_DIR, model_name)
    try:
        if model_path.endswith(".pkl"):
            with open(model_path, "rb") as f:
                return pickle.load(f)
        elif model_path.endswith(".joblib"):
            return joblib.load(model_path)
        else:
            raise ValueError(f"Unsupported model format: {model_path}")
    except Exception as e:
        logger.error(f"Error loading model {model_path}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error loading model: {str(e)}"
        )


def get_model_version(model_name: str) -> str:
    return "1.0.0"


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>ML Model API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px;
                       margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                a { color: #0066cc; }
            </style>
        </head>
        <body>
            <h1>ML Model API</h1>
            <p>API for serving machine learning models</p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    model_name = request.model_name or DEFAULT_MODEL
    model = load_model(model_name)

    try:
        features = request.features

        if hasattr(model, "feature_names_in_"):
            missing_features = set(model.feature_names_in_) - set(
                features.keys()
            )
            if missing_features:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Missing required features: "
                        f"{', '.join(missing_features)}"
                    ),
                )

            X = pd.DataFrame(
                [[features[feature] for feature in model.feature_names_in_]],
                columns=model.feature_names_in_,
            )
        else:
            X = pd.DataFrame([features])

        prediction_result = model.predict(X)[0]

        probability = 0.0
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X)[0]
            prediction_idx = list(model.classes_).index(prediction_result)
            probability = float(probabilities[prediction_idx])

        metrics.record_prediction(
            model_name=model_name.split(".")[0],
            features=features,
            predicted_class=str(prediction_result),
        )

        return {
            "prediction": str(prediction_result),
            "probability": probability,
            "model_name": model_name,
            "model_version": get_model_version(model_name),
        }

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Prediction error: {str(e)}"
        )


@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    return Response(content=metrics.get_metrics(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
