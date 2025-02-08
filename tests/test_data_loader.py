import os
import pytest
import pandas as pd
from io import BytesIO
import requests_mock
from make_data.data_loader import NYCTaxiDataFetcher, ParquetDataSaver, GCSUploader

@pytest.fixture
def requests_mock_fixture():
    with requests_mock.Mocker() as m:
        yield m

@pytest.fixture
def sample_data():
    yield pd.DataFrame({"col1": [1, 2, 3]})

def test_nyc_taxi_data_fetcher_fetch(requests_mock_fixture, sample_data):
    year, month = 2023, 1
    fetcher = NYCTaxiDataFetcher("green")
    url = fetcher._construct_url(year, month)
    
    buffer = BytesIO()
    sample_data.to_parquet(buffer, index=False)
    buffer.seek(0)

    requests_mock_fixture.get(url, content=buffer.getvalue())

    df = fetcher.fetch(year, month)
    assert not df.empty
    assert "col1" in df.columns

def test_nyc_taxi_data_fetcher_fetch_failure(requests_mock_fixture):
    """Test the case where the fetch fails and status code 1 is returned."""
    fetcher = NYCTaxiDataFetcher("green")
    url = fetcher._construct_url(2023, 1)
    requests_mock_fixture.get(url, status_code=404)

    df = fetcher.fetch(2023, 1)
    assert df == 1

def test_parquet_data_saver_save(sample_data):
    saver = ParquetDataSaver()
    file_name = "test.parquet"

    saver.save(sample_data, str(file_name))
    assert os.path.exists(file_name)

    loaded_df = pd.read_parquet(file_name)
    assert loaded_df.equals(sample_data)

def test_parquet_data_saver_cleanup():
    saver = ParquetDataSaver()
    file_name = "test.parquet"

    saver.cleanup(file_name)
    assert not os.path.exists(file_name)

def test_gcs_uploader_upload(mocker, tmp_path):
    mock_client = mocker.patch("google.cloud.storage.Client")
    mock_bucket = mock_client.return_value.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    uploader = GCSUploader("test-bucket")
    uploader.client = mock_client.return_value

    file_name = tmp_path / "test.parquet"
    file_name.touch()

    uploader.upload(str(file_name), "destination/test.parquet")

    mock_blob.upload_from_filename.assert_called_once_with(str(file_name))

def test_gcs_uploader_check_file_exists(mocker):
    mock_client = mocker.patch("google.cloud.storage.Client")
    mock_bucket = mock_client.return_value.bucket.return_value
    mock_blob = mock_bucket.blob.return_value
    mock_blob.exists.return_value = True

    uploader = GCSUploader("test-bucket")
    uploader.client = mock_client.return_value

    assert uploader.check_file_exists("test.parquet") is True
    mock_blob.exists.assert_called_once()
