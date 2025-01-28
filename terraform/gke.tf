# terraform/gke.tf

# Create a GKE cluster within the Free Tier limits
resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1

  # Remove the default node pool to manage node pools separately
  remove_default_node_pool = true

  # Use the existing default VPC network and subnetwork
  network    = "default"
  subnetwork = "default" # Use the existing default subnetwork

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"       # Ensure these secondary ranges exist
    services_secondary_range_name = "services"   # Ensure these secondary ranges exist
  }

  node_config {
    machine_type = "e2-micro"  # Eligible for Free Tier

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}

# Create a node pool with e2-micro instances
resource "google_container_node_pool" "primary_nodes" {
  cluster    = google_container_cluster.primary.name
  location   = var.GCP_REGION
  node_count = 1

  node_config {
    machine_type = "e2-micro"  # Eligible for Free Tier

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  management {
    auto_upgrade = true  # Automatically upgrade nodes to the latest version
    auto_repair  = true  # Automatically repair unhealthy nodes
  }
}
