# terraform/gke.tf

# Create a GKE cluster within the Free Tier limits
resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1

  remove_default_node_pool = true

  ip_allocation_policy {
    # Optional: Specify secondary ranges if you have pre-defined subnets
    # If not, GKE can create them automatically
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  node_config {
    machine_type = "e2-micro"  # Eligible for Free Tier

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  # Optional: Enable additional features as needed
  # For example, enable HTTP/HTTPS load balancing, etc.
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
    auto_upgrade = true
    auto_repair  = true
  }
}
