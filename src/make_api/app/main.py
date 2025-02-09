import os
from functools import lru_cache

import mlflow
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

model_uri = "models:/taxi_fare_prediction.taxi_fare_model@latest-model"


@lru_cache
def get_model(model_uri):
    return mlflow.sklearn.load_model(model_uri)


app = FastAPI()


class InferenceInput(BaseModel):
    passenger_count: int
    trip_type: int
    congestion_surcharge: float
    mean_distance: float
    mean_duration: float
    rush_hour: int
    vendor_id: str


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Taxi Fare Prediction API!", "docs": "/docs"}


@app.post("/predict")
async def predict_one(data: InferenceInput) -> dict[str, float]:
    try:
        df_input = pd.DataFrame([data.dict()])  # pd df might be overkill
        # prediction = get_model(model_uri).predict(df_input)
        pipe = mlflow.sklearn.load_model(model_uri)
        prediction = pipe.predict(df_input)
        return {"prediction": prediction[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}") from e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
