import logging
from io import BytesIO
from typing import Optional

import pandas as pd
from google.cloud import storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GCSConnector:
    def __init__(self, bucket_name: str):
        """
        Create a class to upload data to Google Cloud Storage bucket

        Args:
            bucket_name (str): Name of the bucket
        """
        self.client = storage.Client()
        self.bucket_name = bucket_name

    def upload(self, df: pd.DataFrame, file_name: str):
        """
        Upload file to Google Cloud Storage bucket

        Args:
            file_name (str): Name of the file to upload
            destination (str): Destination path in the bucket
        """
        # TODO: Delete comment on 7th of March if not deleted
        # bucket = self.client.bucket(self.bucket_name)
        # blob = bucket.blob(destination)
        # blob.upload_from_filename(file_name)
        # logging.info(
        #     f"File {file_name} uploaded to gs://{self.bucket_name}/{destination}"
        # )
        destination = f"gs://{self.bucket_name}/{file_name}"
        df.to_parquet(destination)
        logging.info(f"File {file_name} uploaded to {destination}")

    def check_file_exists(self, file_name: str):
        """
        Check if the file exists in the bucket

        Args:
            file_name (str): Name of the file to check
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        return blob.exists()

    def read_many_from_gcs(self, taxi_type: Optional[str] = "green"):
        """Read multiple raw data from GCS"""
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blobs = bucket.list_blobs()
        all_dataframes = []
        for blob in blobs:
            if blob.name.endswith(".parquet") and taxi_type in blob.name:
                content = blob.download_as_bytes()
                df = pd.read_parquet(BytesIO(content))
                all_dataframes.append(df)
        df = pd.concat(all_dataframes, ignore_index=True)
        return df
