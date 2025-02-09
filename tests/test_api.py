import pytest
from fastapi.testclient import TestClient

from make_api.app.main import app

client = TestClient(app)


@pytest.fixture
def sample_input():
    return {
        "passenger_count": 2,
        "trip_type": 1,
        "congestion_surcharge": 2.5,
        "mean_distance": 3.2,
        "mean_duration": 7.5,
        "rush_hour": 1,
        "vendor_id": "VTS",
    }


def test_predict_one(sample_input):
    """Test the predict_one endpoint works"""

    response = client.post("/predict", json=sample_input)

    assert response.status_code == 200

    json_response = response.json()

    assert "prediction" in json_response
    assert isinstance(json_response["prediction"], float)


def test_predict_missing_input():
    """Test the predict_one endpoint fails with missing input"""

    incomplete_input = {
        "passenger_count": 2,
        "trip_type": 1,
        "congestion_surcharge": 2.5,
        "mean_distance": 3.2,
        "rush_hour": 1,
        "vendor_id": "VTS",
    }  # missing mean_duration

    response = client.post("/predict", json=incomplete_input)

    assert response.status_code == 422
