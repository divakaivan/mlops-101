import yaml
import logging
from make_data.data_loader import NYCTaxiDataFetcher, ParquetDataSaver
from make_data.gcs_connector import GCSConnector
from project_config import ProjectConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


config = ProjectConfig.from_yaml("project-config.yaml")
logger.info(yaml.dump(config, default_flow_style=False))

data_fetcher = NYCTaxiDataFetcher(taxi_type=config.taxi_type)
gcs_connector = GCSConnector(bucket_name=config.gcs_raw_data_bucket_name)

for year in config.taxi_data_years:
    for month in config.taxi_data_months:
        data = data_fetcher.fetch(year=year, month=month)
        file_name = f"{config.taxi_type}_tripdata_{year}-{month:02d}.parquet"
        if gcs_connector.check_file_exists(file_name):
            logger.info(f"File {file_name} already exists in GCS bucket. Skipping")
        else:
            data_checker = ParquetDataSaver(data)
            data_checker.validate_schema(config.green_taxi_raw_schema)
            gcs_connector.upload(data, file_name)
