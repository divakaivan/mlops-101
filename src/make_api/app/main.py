import os

import mlflow
import uvicorn
from fastapi import FastAPI

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

model_uri = "models:/taxi_fare_prediction.taxi_fare_model@latest-model"
model = mlflow.sklearn.load_model(model_uri)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "Visit /docs for API documentation"}


@app.get("/predict")
async def predict():
    return {"prediction": "1"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
