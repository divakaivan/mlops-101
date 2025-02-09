import os

import mlflow
import pandas as pd
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

model_uri = "models:/taxi_fare_prediction.taxi_fare_model@latest-model"
pipe = mlflow.sklearn.load_model(model_uri)

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
    return {"Hello": "Visit /docs for API documentation"}


@app.post("/predict")
async def predict_one(data: InferenceInput) -> dict[str, float]:
    df_input = pd.DataFrame([data.dict()])

    prediction = pipe.predict(df_input)

    return {"prediction": prediction[0]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
