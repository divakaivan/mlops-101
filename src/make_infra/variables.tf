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

variable "location_region" {
    description = "Project Location Region"
    default = "asia-northeast3"
}

variable "gcs_raw_taxi_data_bucket_name" {
    description = "Bucket name for raw taxi data"
    default = "mlops_101_raw_taxi_data"
}

variable "gcs_processed_taxi_data_bucket_name" {
    description = "Bucket name for processed taxi data"
    default = "mlops_101_processed_taxi_data"
}

variable "api_logs_bucket" {
    description = "Bucket name for API logs"
    default = "mlops_101_api_logs"
}

variable "gcs_storage_class" {
    description = "Bucket Storage Class"
    default = "STANDARD"
}

variable "mlflow_backend_store_uri" {
    description = "MLflow Backend Store URI"
    default = "sqlite:///mlops_101.sqlite"
}
