import pytest
from pydantic import ValidationError
from tempfile import NamedTemporaryFile
from project_config import ProjectConfig


@pytest.fixture
def valid_yaml_config():
    return """
    gcs_raw_data_bucket_name: "my-bucket"
    taxi_data_years: [2021, 2022]
    taxi_data_months: [1, 2, 3]
    taxi_type: "yellow"
    """


@pytest.fixture
def invalid_yaml_config_missing_field():
    return """
    taxi_data_years: [2021, 2022]
    taxi_data_months: [1, 2, 3]
    taxi_type: "yellow"
    """


@pytest.fixture
def invalid_yaml_config_wrong_type():
    return """
    gcs_raw_data_bucket_name: "my-bucket"
    taxi_data_years: "2021, 2022"  # Should be a list[int], but it's a string
    taxi_data_months: [1, 2, 3]
    taxi_type: "yellow"
    """


def test_project_config_from_valid_yaml(valid_yaml_config):
    with NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(valid_yaml_config)
        temp_file.flush()
        config = ProjectConfig.from_yaml(temp_file.name)

    assert config.gcs_raw_data_bucket_name == "my-bucket"
    assert config.taxi_data_years == [2021, 2022]
    assert config.taxi_data_months == [1, 2, 3]
    assert config.taxi_type == "yellow"


def test_project_config_missing_field(invalid_yaml_config_missing_field):
    with NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(invalid_yaml_config_missing_field)
        temp_file.flush()

        with pytest.raises(ValidationError):
            ProjectConfig.from_yaml(temp_file.name)


def test_project_config_wrong_type(invalid_yaml_config_wrong_type):
    with NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(invalid_yaml_config_wrong_type)
        temp_file.flush()

        with pytest.raises(ValidationError):
            ProjectConfig.from_yaml(temp_file.name)
