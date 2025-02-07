import pandas as pd
from datetime import datetime
from google.cloud import storage

class NYCTaxiDataLoader:
    def __init__(self, start_date: str, end_date: str, bucket_name: str, destination_blob_name: str):
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.bucket_name = bucket_name
        self.destination_blob_name = destination_blob_name
        self.base_url = "https://s3.amazonaws.com/nyc-tlc/trip+data/"
        self.local_file_name = "nyc_taxi_data.csv"

    def generate_date_range(self):
        return pd.date_range(start=self.start_date, end=self.end_date, freq='M')

    def load_data(self):
        date_range = self.generate_date_range()
        data_frames = []
        for date in date_range:
            file_name = f"yellow_tripdata_{date.year}-{date.month:02d}.csv"
            url = self.base_url + file_name
            df = pd.read_csv(url)
            data_frames.append(df)
        return pd.concat(data_frames, ignore_index=True)

    def save_data_to_csv(self, data):
        data.to_csv(self.local_file_name, index=False)

    def upload_to_gcs(self):
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(self.destination_blob_name)
        blob.upload_from_filename(self.local_file_name)
