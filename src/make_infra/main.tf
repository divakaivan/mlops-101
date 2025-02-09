terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.34.0"
    }
  }
}

provider "google" {
  credentials = local.credentials
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "mlops-101-raw-data" {
  name          = var.gcs_raw_taxi_data_bucket_name
  location      = var.location

  storage_class = var.gcs_storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

resource "google_storage_bucket" "mlops-101-processed-data" {
  name          = var.gcs_processed_taxi_data_bucket_name
  location      = var.location

  storage_class = var.gcs_storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

resource "google_storage_bucket" "mlops-101-api-logs" {
  name          = var.api_logs_bucket
  location      = var.location

  storage_class = var.gcs_storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

resource "google_compute_instance" "mlops-101-mlflow-server" {
  name         = "mlops-101-mlflow-server"
  machine_type = "e2-small"
  zone         = var.region

  boot_disk {
    initialize_params {
      image = "projects/ml-images/global/images/c0-deeplearning-common-cpu-v20240613-debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral IP
    }
  }

  tags = ["mlflow"]

  metadata_startup_script = <<-EOT
    #!/bin/bash
    echo "Startup script running..." >> /var/log/startup-script.log 2>&1
    apt-get update >> /var/log/startup-script.log 2>&1
    apt-get install -y python3-pip >> /var/log/startup-script.log 2>&1
    pip3 install mlflow==2.20.1 >> /var/log/startup-script.log 2>&1
    pip3 install google-cloud-storage >> /var/log/startup-script.log 2>&1
    mlflow server --backend-store-uri ${var.mlflow_backend_store_uri} -h 0.0.0.0 -p 5000 >> /var/log/startup-script.log 2>&1
    echo "MLflow server started" >> /var/log/startup-script.log 2>&1
    EOT
}

resource "google_compute_firewall" "mlflow-server-firewall" {
  name    = "mlflow-server-firewall"
  network = "default"
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["22", "5000"]
  }

  target_tags = ["mlflow"]
  source_ranges = [ "0.0.0.0/0" ]
}

resource "google_artifact_registry_repository" "fastapi-taxi-fare-predictor" {
  location      = var.location_region
  repository_id = "fastapi-taxi-fare-predictor"
  description   = "FastAPI Taxi Fare Predictor"
  format        = "DOCKER"
}

resource "google_container_cluster" "mlops-101-my-autopilot-cluster" {
  name     = "mlops-101-my-autopilot-cluster"
  location = var.location_region
  project  = var.project
  enable_autopilot = true
  deletion_protection = false
}

resource "google_logging_project_sink" "model_api_logs_to_gcs" {
  name = "model_api_logs_to_gcs"
  destination = "storage.googleapis.com/${var.api_logs_bucket}"
  filter = "SEARCH(\"[Prediction Input]\") OR SEARCH(\"[Prediction Output]\")"
  unique_writer_identity = true
}
