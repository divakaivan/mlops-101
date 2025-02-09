import os
from io import BytesIO

import pandas as pd
import pytest
import requests_mock

from make_data.data_loader import NYCTaxiDataFetcher, ParquetDataSaver


@pytest.fixture
def requests_mock_fixture():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def sample_data():
    yield pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "salary": [50000.0, 60000.0, 70000.0],
        }
    )


@pytest.fixture
def valid_schema():
    yield [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"},
        {"name": "salary", "type": "float"},
    ]


def test_nyc_taxi_data_fetcher_fetch(requests_mock_fixture, sample_data):
    """Test the case where the fetch is successful."""
    year, month = 2023, 1
    fetcher = NYCTaxiDataFetcher("green")
    url = fetcher._construct_url(year, month)

    buffer = BytesIO()
    sample_data.to_parquet(buffer, index=False)
    buffer.seek(0)

    requests_mock_fixture.get(url, content=buffer.getvalue())

    df = fetcher.fetch(year, month)
    assert not df.empty
    assert "id" in df.columns


def test_nyc_taxi_data_fetcher_fetch_failure(requests_mock_fixture):
    """Test the case where the fetch fails and status code 1 is returned."""
    fetcher = NYCTaxiDataFetcher("green")
    url = fetcher._construct_url(2023, 1)
    requests_mock_fixture.get(url, status_code=404)

    df = fetcher.fetch(2023, 1)
    assert df == 1


def test_parquet_data_saver_save(sample_data):
    """Test the case where the data is saved successfully."""
    saver = ParquetDataSaver(sample_data)
    file_name = "test.parquet"

    saver.save(str(file_name))
    assert os.path.exists(file_name)

    loaded_df = pd.read_parquet(file_name)
    assert loaded_df.equals(sample_data)


def test_validate_schema_success(sample_data, valid_schema):
    """Test the case where the schema is valid."""
    validator = ParquetDataSaver(sample_data)
    validator.validate_schema(valid_schema)
    assert sample_data["id"].dtype == "int64"
    assert sample_data["name"].dtype == "object"
    assert sample_data["age"].dtype == "int64"
    assert sample_data["salary"].dtype == "float64"


def test_missing_columns(sample_data, valid_schema):
    """Test the case where the schema is missing columns."""
    sample_data.drop(columns=["age"], inplace=True)
    validator = ParquetDataSaver(sample_data)
    with pytest.raises(ValueError, match="Missing columns: {'age'}"):
        validator.validate_schema(valid_schema)


def test_extra_columns(sample_data, valid_schema):
    """Test the case where the schema has extra columns."""
    sample_data["extra"] = [1, 2, 3]
    validator = ParquetDataSaver(sample_data)
    with pytest.raises(ValueError, match="Extra columns: {'extra'}"):
        validator.validate_schema(valid_schema)


def test_unsupported_type(sample_data):
    """Test the case where the schema has an unsupported type."""
    invalid_schema = [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"},
        {"name": "salary", "type": "boolean"},
    ]
    validator = ParquetDataSaver(sample_data)
    with pytest.raises(ValueError, match="Unsupported type boolean for column 'salary'"):
        validator.validate_schema(invalid_schema)


def test_parquet_data_saver_cleanup(sample_data):
    """Test the case where the file is removed successfully."""
    saver = ParquetDataSaver(sample_data)
    file_name = "test.parquet"

    saver.cleanup(file_name)
    assert not os.path.exists(file_name)
