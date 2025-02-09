from unittest.mock import MagicMock

import pandas as pd
import pytest

from make_data.data_processor import DataProcessor


@pytest.fixture
def sample_dataframe():
    data = {
        "lpep_pickup_datetime": ["2024-02-08 10:00:00", "2024-02-08 15:00:00"],
        "lpep_dropoff_datetime": ["2024-02-08 10:15:00", "2024-02-08 15:30:00"],
        "fare_amount": [10, -5],
        "PULocationID": [1, 2],
        "DOLocationID": [3, 4],
        "trip_distance": [2.5, 3.5],
        "VendorID": [1, 2],
    }
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.num_features = ["fare_amount", "trip_distance"]
    config.cat_features = ["vendor_id"]
    config.target = ["duration"]
    return config


def test_process_data(sample_dataframe, mock_config):
    """Test the process_data method"""

    processor = DataProcessor(sample_dataframe, mock_config)
    processor.process_data()

    assert "duration" in processor.df.columns
    assert "vendor_id" in processor.df.columns
    assert processor.df["fare_amount"].min() >= 0
    assert processor.df["duration"].min() >= 0


def test_split_data(sample_dataframe, mock_config):
    """Test the split_data method"""

    processor = DataProcessor(sample_dataframe, mock_config)
    processor.process_data()
    train, test = processor.split_data()

    assert len(train) > 0
    assert len(test) > 0
    assert len(train) + len(test) == len(processor.df)
