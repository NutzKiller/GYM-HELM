# terraform/gke.tf

# Create a subnetwork with secondary ranges
resource "google_compute_subnetwork" "default" {
  name          = "default"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.GCP_REGION
  network       = "default" # Ensure this matches your network name

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/20"
  }
}

# Create a GKE cluster within the Free Tier limits
resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1

  # Remove the default node pool to manage node pools separately
  remove_default_node_pool = true

  # Explicitly specify the default VPC network and subnetwork
  network    = "default"
  subnetwork = google_compute_subnetwork.default.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  node_config {
    machine_type = "e2-micro"  # Eligible for Free Tier

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    # (Optional) Specify additional configurations such as labels or tags
    # labels = {
    #   environment = "production"
    # }
  }

  # (Optional) Enable additional features as needed
  # For example, enable HTTP/HTTPS load balancing, etc.
  # enable_autorepair = true
  # enable_autoupgrade = true
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

    # (Optional) Specify additional configurations such as labels or tags
    # labels = {
    #   role = "worker"
    # }
  }

  management {
    auto_upgrade = true  # Automatically upgrade nodes to the latest version
    auto_repair  = true  # Automatically repair unhealthy nodes
  }

  # (Optional) Specify additional node pool configurations
  # For example, specify taints or local SSDs
  # taints = [{
  #   key    = "key"
  #   value  = "value"
  #   effect = "NO_SCHEDULE"
  # }]
}
