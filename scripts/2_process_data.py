import yaml
import logging
from make_data.data_processor import DataProcessor
from make_data.gcs_connector import GCSConnector
from project_config import ProjectConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


config = ProjectConfig.from_yaml("project-config.yaml")
logger.info(yaml.dump(config, default_flow_style=False))

raw_gcs_bucket_connector = GCSConnector(bucket_name=config.gcs_raw_data_bucket_name)

df = raw_gcs_bucket_connector.read_many_from_gcs(taxi_type="green")
data_processor = DataProcessor(df=df, config=config)
data_processor.process_data()
train_set, test_set = data_processor.split_data(test_size=0.2, random_state=42)

processed_gcs_bucket_connector = GCSConnector(
    bucket_name=config.gcs_processed_taxi_data_bucket_name
)
train_file_name = "green_taxi_train_set.parquet"
processed_gcs_bucket_connector.upload(train_set, train_file_name)
test_file_name = "green_taxi_test_set.parquet"
processed_gcs_bucket_connector.upload(test_set, test_file_name)
