from typing import Optional

import yaml
from pydantic import BaseModel


class ProjectConfig(BaseModel):
    """Project configuration"""

    gcs_raw_data_bucket_name: str
    gcs_processed_taxi_data_bucket_name: str
    taxi_data_years: list[int]
    taxi_data_months: list[int]
    taxi_type: str
    green_taxi_raw_schema: list[dict]
    num_features: list[str]
    cat_features: Optional[list[str]]
    target: list[str]

    @classmethod
    def from_yaml(cls, config_path: str):
        """Load configuration from yaml file"""
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
