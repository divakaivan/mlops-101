from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from mlflow.tracking import MlflowClient

from make_model.model_trainer import ModelTrainer


def create_dummy_data():
    data = {
        "vendor_id": [1, 2, 1, 2, 1],
        "feature1": [10, 20, 30, 40, 50],
        "feature2": [5, 15, 25, 35, 45],
        "fare_amount": [12, 22, 32, 42, 52],
    }
    df = pd.DataFrame(data)
    return df.iloc[:3], df.iloc[3:]


@pytest.fixture
def setup_trainer():
    train_set, test_set = create_dummy_data()
    config = MagicMock()
    config.experiment_name = "test_experiment"
    config.num_features = ["feature1", "feature2"]
    config.cat_features = ["vendor_id"]
    config.target = "fare_amount"

    tags = MagicMock()
    tags.git_sha = "test_sha"
    tags.branch = "test_branch"
    return ModelTrainer(train_set, test_set, config, tags)


def test_feature_engineering(setup_trainer):
    """Test feature engineering method"""
    trainer = setup_trainer
    trainer.feature_engineering()

    assert not trainer.X_train.empty
    assert not trainer.X_test.empty
    assert not trainer.y_train.empty
    assert not trainer.y_test.empty
    assert trainer.X_train.shape[1] == 3
    assert trainer.y_train.shape[0] == 3


def test_register_model(setup_trainer):
    """Test register model method"""
    trainer = setup_trainer
    trainer.run_id = "test_run_id"

    with (
        patch("mlflow.register_model", return_value=MagicMock(version=1)) as mock_register,
        patch.object(MlflowClient, "set_registered_model_alias") as mock_alias,
    ):
        trainer.register_model()

        mock_register.assert_called_once()
        mock_alias.assert_called_once()
