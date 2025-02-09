import logging
import os
from functools import lru_cache
from typing import Literal

import mlflow
import pandas as pd
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

model_uri = "models:/taxi_fare_prediction.taxi_fare_model@latest-model"


@lru_cache
def get_model(model_uri):
    return mlflow.sklearn.load_model(model_uri)


app = FastAPI()


class PredictionInput(BaseModel):
    passenger_count: int
    trip_type: int
    congestion_surcharge: float
    mean_distance: float
    mean_duration: float
    rush_hour: int
    vendor_id: str


class OutputItem(BaseModel):
    prediction_input: PredictionInput
    prediction: float
    status: Literal["success", "warning", "failure"]
    message: str


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Taxi Fare Prediction API!", "docs": "/docs"}


@app.post("/predict")
async def predict_one(data: PredictionInput) -> OutputItem:
    try:
        df_input = pd.DataFrame([data.dict()])  # pd df might be overkill
        logger.info(f"[Prediction Input] Received input: {df_input}")
        prediction = get_model(model_uri).predict(df_input)

        if prediction[0] <= 0:
            logger.error("[Prediction Output] Prediction failed: Negative prediction")
            return OutputItem(
                prediction_input=data,
                prediction=0.0,
                status="warning",
                message="Prediction failed: Negative prediction. Check your inputs.",
            )
        else:
            logger.info(f"[Prediction Output] Prediction: {prediction[0]}")
            return OutputItem(
                prediction_input=data, prediction=prediction[0], status="success", message="Prediction successful"
            )

    except Exception as e:
        logger.error(f"[Prediction Output] Prediction failed: {str(e)}")
        return OutputItem(
            prediction_input=data, prediction=-1.0, status="failure", message=f"Prediction failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
