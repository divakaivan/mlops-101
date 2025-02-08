locals {
  credentials = "/Users/ivanivanov/.gcp/mlops-101-creds.json"
}

variable "region" {
  description = "Region"
  default     = "asia-northeast3-a"
}

variable "project" {
  description = "Project"
  default     = "mlops-101"
}

variable "location" {
    description = "Project Location"
    default = "ASIA"
}

variable "gcs_raw_taxi_data_bucket_name" {
    description = "Bucket name for raw taxi data"
    default = "mlops_101_raw_taxi_data"
}

variable "gcs_processed_taxi_data_bucket_name" {
    description = "Bucket name for processed taxi data"
    default = "mlops_101_processed_taxi_data"
}

variable "gcs_storage_class" {
    description = "Bucket Storage Class"
    default = "STANDARD"
}

variable "mlops_101_mlflow_artifacts" {
    description = "Bucket name for MLflow artifacts"
    default = "mlops_101_mlflow_artifacts"
}

variable "mlflow_backend_store_uri" {
    description = "MLflow Backend Store URI"
    default = "sqlite:///mlops_101.sqlite"
}

variable "mlflow_artifact_location" {
    description = "MLflow Artifact Location"
    default = "gs://mlops_101_mlflow_artifacts"
}
