import logging
from typing import Optional, Union
import pandas as pd
from sklearn.model_selection import train_test_split
from project_config import ProjectConfig
from utils import outlier_imputer, rush_hourizer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, df: pd.DataFrame, config: ProjectConfig):
        """
        Class to process taxi data for model training

        Args:
            config (ProjectConfig): ProjectConfig object
        """
        self.df = df
        self.config = config

    def process_data(self):
        """Process raw data"""
        self.df.drop_duplicates(inplace=True)

        self.df["lpep_pickup_datetime"] = pd.to_datetime(
            self.df["lpep_pickup_datetime"]
        )
        self.df["lpep_dropoff_datetime"] = pd.to_datetime(
            self.df["lpep_dropoff_datetime"]
        )

        self.df["duration"] = (
            self.df["lpep_dropoff_datetime"] - self.df["lpep_pickup_datetime"]
        )
        self.df["duration"] = self.df["duration"].dt.total_seconds() // 60

        self.df.loc[self.df["fare_amount"] < 0, "fare_amount"] = 0
        self.df.loc[self.df["duration"] < 0, "duration"] = 0

        self.df = outlier_imputer(self.df, ["fare_amount"], 6)
        self.df = outlier_imputer(self.df, ["duration"], 6)

        self.df["pickup_dropoff"] = (
            self.df["PULocationID"].astype(str)
            + " "
            + self.df["DOLocationID"].astype(str)
        )
        grouped = self.df.groupby("pickup_dropoff").mean(numeric_only=True)[
            ["trip_distance"]
        ]
        grouped_dict = grouped.to_dict()["trip_distance"]
        self.df["mean_distance"] = self.df["pickup_dropoff"]
        self.df["mean_distance"] = self.df["mean_distance"].map(grouped_dict)

        grouped = self.df.groupby("pickup_dropoff").mean(numeric_only=True)[
            ["duration"]
        ]
        grouped_dict = grouped.to_dict()["duration"]
        self.df["mean_duration"] = self.df["pickup_dropoff"]
        self.df["mean_duration"] = self.df["mean_duration"].map(grouped_dict)

        self.df["day"] = self.df["lpep_pickup_datetime"].dt.day_name().str.lower()
        self.df["month"] = self.df["lpep_pickup_datetime"].dt.strftime("%b").str.lower()
        self.df["rush_hour"] = self.df["lpep_pickup_datetime"].dt.hour
        self.df.loc[self.df["day"].isin(["saturday", "sunday"]), "rush_hour"] = 0

        self.df["rush_hour"] = self.df["rush_hour"].astype(int)
        mask = (self.df["day"] != "saturday") & (self.df["day"] != "sunday")
        self.df.loc[mask, "rush_hour"] = self.df.loc[mask].apply(rush_hourizer, axis=1)

        self.df.rename(columns={"VendorID": "vendor_id"}, inplace=True)

        relevant_cols = self.config.num_features + self.config.target

        self.df = self.df.loc[:, relevant_cols]
        self.df.dropna(inplace=True)

    def split_data(
        self, test_size: Optional[float] = 0.2, random_state: Optional[int] = 42
    ) -> Union[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets

        Args:
            test_size (float, optional): Size of test set. Defaults to 0.2.
            random_state (int, optional): Random state. Defaults to 42.

        Returns:
            Union[pd.DataFrame, pd.DataFrame]: Train and test pandas dataframes
        """

        train_set, test_set = train_test_split(
            self.df, test_size=test_size, random_state=random_state
        )
        return train_set, test_set
