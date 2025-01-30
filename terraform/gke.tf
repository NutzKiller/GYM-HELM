# terraform/gke.tf

# Create a GKE cluster
resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 2  # Increased for better scheduling

  remove_default_node_pool = true

  # Use the existing default VPC network and subnetwork
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

# Create a node pool with auto-scaling enabled
resource "google_container_node_pool" "primary_nodes" {
  cluster  = google_container_cluster.primary.name
  location = var.GCP_REGION

  # Enable auto-scaling
  autoscaling {
    min_node_count = 2
    max_node_count = 3
  }

  node_config {
    machine_type = "e2-medium"  # Upgraded from e2-micro to e2-medium (4GB RAM)
    disk_size_gb = 20           # Increased disk space for better performance

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}
