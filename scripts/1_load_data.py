import logging
from make_data.data_loader import NYCTaxiDataFetcher, ParquetDataSaver, GCSUploader
from project_config import ProjectConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


config = ProjectConfig.from_yaml("project-config.yaml")

data_fetcher = NYCTaxiDataFetcher(taxi_type=config.taxi_type)
data_saver = ParquetDataSaver()
gcs_uploader = GCSUploader(bucket_name=config.gcs_raw_data_bucket_name)

for year in config.taxi_data_years:
    for month in config.taxi_data_months:
        data = data_fetcher.fetch(year=year, month=month)
        file_name = f"{config.taxi_type}_tripdata_{year}-{month:02d}.parquet"
        if gcs_uploader.check_file_exists(file_name):
            logger.info(f"File {file_name} already exists in GCS bucket. Skipping")
        else:
            data_saver.save(data, file_name)
            gcs_uploader.upload(file_name, f"{file_name}")
            data_saver.cleanup(file_name)
