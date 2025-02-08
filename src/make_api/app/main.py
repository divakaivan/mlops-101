# model_uri = f"models:/{model_name}@{model_version_alias}"
# model = mlflow.sklearn.load_model(model_uri)

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "CICD World"}


@app.get("/predict")
async def predict():
    return {"prediction": "1"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
