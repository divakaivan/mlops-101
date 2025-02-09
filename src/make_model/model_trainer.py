import logging

import mlflow
import pandas as pd
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from project_config import ProjectConfig, Tags

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self, train_set: pd.DataFrame, test_set: pd.DataFrame, config: ProjectConfig, tags: Tags):
        self.config = config
        self.tags = tags.dict()
        self.train_set = train_set
        self.test_set = test_set
        self.artifact_path = "linear-reg-pipe"

    def feature_engineering(self):
        self.train_set["vendor_id"] = self.train_set["vendor_id"].astype(str)
        self.test_set["vendor_id"] = self.test_set["vendor_id"].astype(str)

        self.X_train = self.train_set[self.config.num_features + self.config.cat_features]
        self.y_train = self.train_set[self.config.target]
        self.X_test = self.test_set[self.config.num_features + self.config.cat_features]
        self.y_test = self.test_set[self.config.target]

        logger.info(f"X_train shape: {self.X_train.shape}")
        logger.info(f"y_train shape: {self.y_train.shape}")
        logger.info(f"X_test shape: {self.X_test.shape}")
        logger.info(f"y_test shape: {self.y_test.shape}")

        logger.info("Feature Engineering Done")

    def train(self):
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), self.config.num_features),
                ("cat", OneHotEncoder(handle_unknown="ignore"), self.config.cat_features),
            ]
        )
        pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", LinearRegression())])
        logging.info("Starting MLFlow Run")
        mlflow.set_experiment(self.config.experiment_name)
        with mlflow.start_run(tags=self.tags) as run:
            self.run_id = run.info.run_id
            logging.info("Fitting the model")

            pipe.fit(self.X_train, self.y_train)
            logging.info("Running predictions")
            y_pred = pipe.predict(self.X_test)

            rmse = root_mean_squared_error(self.y_test, y_pred)
            mae = mean_absolute_error(self.y_test, y_pred)
            r2 = r2_score(self.y_test, y_pred)

            logger.info(f"Root Mean Squared Error: {rmse}")
            logger.info(f"Mean Absolute Error: {mae}")
            logger.info(f"R2 Score: {r2}")

            mlflow.log_param("model_type", "Linear Regression with preprocessing")
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("r2_score", r2)
            signature = infer_signature(self.X_train, y_pred)

            mlflow_train_set = mlflow.data.from_pandas(self.train_set)
            mlflow.log_input(mlflow_train_set, context="training", tags={"name_detail": self.config.train_file_name})
            mlflow.sklearn.log_model(
                sk_model=pipe,
                artifact_path=self.artifact_path,
                input_example=self.X_train.head(1),
                signature=signature,
            )

    def register_model(self):
        registered_model = mlflow.register_model(
            model_uri=f"runs:/{self.run_id}/{self.artifact_path}",
            name=f"{self.config.experiment_name}.taxi_fare_model",
            tags=self.tags,
        )

        latest_version = registered_model.version

        client = MlflowClient()
        client.set_registered_model_alias(
            name=f"{self.config.experiment_name}.taxi_fare_model",
            alias="latest-model",
            version=latest_version,
        )
