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
