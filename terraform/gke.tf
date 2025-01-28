# terraform/gke.tf

# Create a GKE cluster within the Free Tier limits
resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1

  # Remove the default node pool to manage node pools separately
  remove_default_node_pool = true

  # Explicitly specify the default VPC network
  network    = "default"  # Ensure this matches the name of your recreated VPC network

  ip_allocation_policy {
    # Specify secondary ranges if they exist in the default subnet
    # These should be automatically created if you used --subnet-mode=auto
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
