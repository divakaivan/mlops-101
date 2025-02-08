import argparse
import logging
import os

import mlflow

from make_data.gcs_connector import GCSConnector
from make_model.model_trainer import ModelTrainer
from project_config import ProjectConfig, Tags

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--git_sha",
    action="store",
    default=None,
    type=str,
    required=True,
)
parser.add_argument(
    "--git_branch",
    action="store",
    default=None,
    type=str,
    required=True,
)
args = parser.parse_args()

config = ProjectConfig.from_yaml("project-config.yaml")

tags_dict = {"git_sha": args.git_sha, "branch": args.git_branch}
tags = Tags(**tags_dict)

gcs = GCSConnector(bucket_name=config.gcs_processed_taxi_data_bucket_name)
train_set = gcs.read_one_from_gcs(config.train_file_name)
test_set = gcs.read_one_from_gcs(config.test_file_name)

trainer = ModelTrainer(train_set=train_set, test_set=test_set, config=config, tags=tags)

trainer.feature_engineering()

trainer.train()

trainer.register_model()
