# terraform/gke.tf

# Create a subnetwork with secondary ranges
resource "google_compute_subnetwork" "default" {
  name          = "default"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.GCP_REGION
  network       = "default"

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/20"
  }
}

# Create a GKE cluster
resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1

  remove_default_node_pool = true

  network    = "default"
  subnetwork = google_compute_subnetwork.default.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  # Addons configuration for HTTP load balancing
  addons_config {
    http_load_balancing {
      disabled = false
    }
  }
}

# Create a node pool
resource "google_container_node_pool" "primary_nodes" {
  cluster    = google_container_cluster.primary.name
  location   = var.GCP_REGION
  node_count = 1

  node_config {
    machine_type = "e2-micro"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}