import os
import pandas as pd
from google.cloud import storage
from abc import ABC, abstractmethod
import requests
from io import BytesIO
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataSaver(ABC):
    @abstractmethod
    def save(self, data: pd.DataFrame, file_name: str):
        pass

    @abstractmethod
    def cleanup(self, file_name: str):
        pass


class NYCTaxiDataFetcher:
    BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/"

    def __init__(self, taxi_type: str = "green"):
        """
        Create a class for fetching NYC Taxi data.

        Args:
            taxi_type (str, optional): Type of taxi data (e.g., "green", "yellow"). Defaults to "green".
        """
        self.taxi_type = taxi_type

    def _construct_url(self, year: int, month: int) -> str:
        """Constructs the URL dynamically for a given year and month."""
        file_name = f"{self.taxi_type}_tripdata_{year}-{month:02d}.parquet"
        return self.BASE_URL + file_name

    def fetch(self, year: int, month: int) -> pd.DataFrame:
        """
        Fetches the Parquet file and loads it into a Pandas DataFrame.
        Assumes data comes in Parquet format.

        Args:
            year (int): Year for which to fetch the data (e.g., 2020)
            month (int): Month for which to fetch the data (e.g., 1 for January)

        Returns:
            pd.DataFrame: Pandas DataFrame containing the fetched data.
        """
        url = self._construct_url(year, month)

        try:
            response = requests.get(url)
            response.raise_for_status()
            return pd.read_parquet(BytesIO(response.content))

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")

        except pd.errors.EmptyDataError:
            logger.error(f"No data found at {url}")


class ParquetDataSaver(DataSaver):
    def save(self, data: pd.DataFrame, file_name: str):
        """
        Save pandas data to parquet file.
        Currently only accepts pandas dataframes.

        Args:
            data (pd.DataFrame): Dataframe to save
            file_name (str): Name of the file
        """
        data.to_parquet(file_name, index=False)
        logging.info(f"Data saved to {file_name}")

    def cleanup(self, file_name: str):
        """
        Remove the saved parquet file from local storage.

        Args:
            file_name (str): Name of the file to remove
        """
        if os.path.exists(file_name):
            os.remove(file_name)
            logging.info(f"File {file_name} removed successfully.")
        else:
            logging.info(f"File {file_name} does not exist.")


class GCSUploader:
    def __init__(self, bucket_name: str):
        """
        Create a class to upload data to Google Cloud Storage bucket

        Args:
            bucket_name (str): Name of the bucket
        """
        self.client = storage.Client()
        self.bucket_name = bucket_name

    def upload(self, file_name: str, destination: str):
        """
        Upload file to Google Cloud Storage bucket

        Args:
            file_name (str): Name of the file to upload
            destination (str): Destination path in the bucket
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination)
        blob.upload_from_filename(file_name)
        logging.info(
            f"File {file_name} uploaded to gs://{self.bucket_name}/{destination}"
        )

    def check_file_exists(self, file_name: str):
        """
        Check if the file exists in the bucket

        Args:
            file_name (str): Name of the file to check
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        return blob.exists()
