import pandas as pd
from google.cloud import storage
from abc import ABC, abstractmethod
import requests
from io import BytesIO


class DataSaver(ABC):
    @abstractmethod
    def save(self, data: pd.DataFrame, file_name: str):
        pass


class NYCTaxiDataFetcher:
    BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/"

    def __init__(self, taxi_type: str = "green"):
        """
        Constructor for fetching NYC Taxi data.

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

        Raises:
            ValueError: If the request fails or no data is found.

        Returns:
            pd.DataFrame: Pandas DataFrame containing the fetched data.
        """
        url = self._construct_url(year, month)

        try:
            response = requests.get(url)
            response.raise_for_status()  
            return pd.read_parquet(BytesIO(response.content))

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request failed: {e}")

        except pd.errors.EmptyDataError:
            raise ValueError(f"No data found at {url}")

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
        print(f"Data saved to {file_name}")


class GCSUploader:
    def __init__(self, bucket_name: str):
        """
        (Constructor) Upload data to Google Cloud Storage bucket

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
        print(f"File {file_name} uploaded to gs://{self.bucket_name}/{destination}")
