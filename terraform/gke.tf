locals {
  update_trigger = timestamp()
}

resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1  # Increased for better scheduling

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

resource "google_container_node_pool" "primary_nodes" {
  cluster  = google_container_cluster.primary.name
  location = var.GCP_REGION

  autoscaling {
    min_node_count = 2
    max_node_count = 2
  }

  node_config {
    machine_type = "e2-medium"   # Upgraded from e2-micro to e2-medium (4GB RAM)
    disk_size_gb = 15            # Increased disk space for better performance
    disk_type    = "pd-standard"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
    image_type = "COS_CONTAINERD"  # Specify the node image type
    resource_labels = {
      dummy = local.update_trigger  # This value changes each plan, forcing an update.
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
