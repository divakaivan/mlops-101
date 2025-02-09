import logging
import os

import pandas as pd
from evidently.future.datasets import DataDefinition, Dataset
from evidently.future.presets import DataSummaryPreset
from evidently.future.report import Report
from evidently.ui.workspace.cloud import CloudWorkspace

from make_data.gcs_connector import GCSConnector
from project_config import ProjectConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

config = ProjectConfig.from_yaml("project-config.yaml")

gcs = GCSConnector(bucket_name=config.gcs_processed_taxi_data_bucket_name)

ws = CloudWorkspace(token=os.getenv("EVIDENTLY_API_TOKEN"), url="https://app.evidently.cloud")

project = ws.get_project(os.getenv("EVIDENTLY_PROJECT_ID"))

latest_train_data = gcs.read_one_from_gcs(config.train_file_name)
latest_test_data = gcs.read_one_from_gcs(config.test_file_name)

schema = DataDefinition(numerical_columns=config.num_features + config.target, categorical_columns=config.cat_features)

eval_data_1 = Dataset.from_pandas(pd.DataFrame(latest_train_data), data_definition=schema)

eval_data_2 = Dataset.from_pandas(pd.DataFrame(latest_test_data), data_definition=schema)

report = Report([DataSummaryPreset()], include_tests="True")
my_eval = report.run(eval_data_1, eval_data_2)
ws.add_run(project.id, my_eval, include_data=False)

logger.info("Dashboard created successfully")
