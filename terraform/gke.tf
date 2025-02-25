terraform {
  backend "gcs" {
    bucket = "tfstate_gymproject"
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.7"
    }
  }

  required_version = ">= 1.0.0"
}

# Data source to get a current timestamp offset (always updated)
data "time_offset" "now" {
  offset_seconds = 0
}

resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1

  remove_default_node_pool = true

  network    = "default"
  subnetwork = "default"

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  addons_config {
    http_load_balancing {
      disabled = false
    }
  }
}

resource "google_container_node_pool" "primary_nodes" {
  cluster  = google_container_cluster.primary.name
  location = var.GCP_REGION

  autoscaling {
    min_node_count = 2
    max_node_count = 2
  }

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 15
    disk_type    = "pd-standard"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
    image_type = "COS_CONTAINERD"
    resource_labels = {
      dummy = data.time_offset.now.rfc3339
    }
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}
