import pandas as pd
import logging
from make_data.gcs_connector import GCSConnector
from unittest.mock import patch, MagicMock


def test_gcs_connector_upload(mocker, caplog):
    """Test the upload method of the GCSConnector class."""

    mock_client = mocker.patch("google.cloud.storage.Client")
    mock_to_parquet = mocker.patch("pandas.DataFrame.to_parquet")

    uploader = GCSConnector("test-bucket")
    uploader.client = mock_client.return_value

    df = pd.DataFrame({"col1": [1, 2, 3]})
    file_name = "test.parquet"

    with caplog.at_level(logging.INFO):
        uploader.upload(df, file_name)

    expected_path = f"gs://test-bucket/{file_name}"

    mock_to_parquet.assert_called_once_with(expected_path)


def test_gcs_connector_check_file_exists(mocker):
    """Test the check_file_exists method of the GCSConnector class."""
    mock_client = mocker.patch("google.cloud.storage.Client")
    mock_bucket = mock_client.return_value.bucket.return_value
    mock_blob = mock_bucket.blob.return_value
    mock_blob.exists.return_value = True

    uploader = GCSConnector("test-bucket")
    uploader.client = mock_client.return_value

    assert uploader.check_file_exists("test.parquet") is True
    mock_blob.exists.assert_called_once()


@patch("make_data.gcs_connector.storage.Client")
def test_read_many_from_gcs(mock_storage_client):
    """Test the read_many_from_gcs method of the GCSConnector class."""
    mock_client_instance = mock_storage_client.return_value
    mock_bucket = mock_client_instance.bucket.return_value
    mock_blob1 = MagicMock()
    mock_blob1.name = "green_taxi_data_1.parquet"
    mock_blob1.download_as_bytes.return_value = pd.DataFrame(
        {"col1": [1, 2]}
    ).to_parquet()

    mock_blob2 = MagicMock()
    mock_blob2.name = "green_taxi_data_2.parquet"
    mock_blob2.download_as_bytes.return_value = pd.DataFrame(
        {"col1": [3, 4]}
    ).to_parquet()

    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]

    instance = GCSConnector("test-bucket")
    df = instance.read_many_from_gcs(taxi_type="green")

    expected_df = pd.DataFrame({"col1": [1, 2, 3, 4]})
    pd.testing.assert_frame_equal(df, expected_df)
