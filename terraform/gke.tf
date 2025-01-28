# Create a GKE cluster within the Free Tier limits

resource "google_container_cluster" "primary" {
  name               = "gym-cluster"
  location           = var.GCP_REGION
  initial_node_count = 1

  node_config {
    machine_type = "e2-micro"  # Eligible for Free Tier

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  # Enable Kubernetes API features as needed
  enable_ip_alias = true

  # Remove the default node pool and create a separate one
  remove_default_node_pool = true
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
}

# Get current client configuration
data "google_client_config" "current" {}

# Configure Kubernetes provider
provider "kubernetes" {
  host                   = google_container_cluster.primary.endpoint
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth.0.cluster_ca_certificate)
  token                  = data.google_client_config.current.access_token
}

# Create a Kubernetes namespace
resource "kubernetes_namespace" "gym" {
  metadata {
    name = "gym-namespace"
  }
}

# Create a Kubernetes ConfigMap
resource "kubernetes_config_map" "gym_config" {
  metadata {
    name      = "gym-config"
    namespace = kubernetes_namespace.gym.metadata[0].name
  }

  data = {
    DATABASE_URL = var.DATABASE_URL
  }
}

# Create a Kubernetes Secret
resource "kubernetes_secret" "gym_secret" {
  metadata {
    name      = "gym-secret"
    namespace = kubernetes_namespace.gym.metadata[0].name
  }

  data = {
    SECRET_KEY = base64encode(var.SECRET_KEY)
  }
}

# Deploy the application using Deployment
resource "kubernetes_deployment" "gym_deployment" {
  metadata {
    name      = "gym-deployment"
    namespace = kubernetes_namespace.gym.metadata[0].name
    labels = {
      app = "gym"
    }
  }

  spec {
    replicas = 1  # Single replica to stay within Free Tier

    selector {
      match_labels = {
        app = "gym"
      }
    }

    template {
      metadata {
        labels = {
          app = "gym"
        }
      }

      spec {
        container {
          name  = "gym-container"
          image = "nutzkiller/gym:latest"

          ports {
            container_port = 5000
          }

          env {
            name  = "DATABASE_URL"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.gym_config.metadata[0].name
                key  = "DATABASE_URL"
              }
            }
          }

          env {
            name  = "SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.gym_secret.metadata[0].name
                key  = "SECRET_KEY"
              }
            }
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 15
            period_seconds        = 20
          }
        }
      }
    }
  }
}

# Expose the Deployment using a Service of type LoadBalancer
resource "kubernetes_service" "gym_service" {
  metadata {
    name      = "gym-service"
    namespace = kubernetes_namespace.gym.metadata[0].name
  }

  spec {
    type = "LoadBalancer"

    selector = {
      app = kubernetes_deployment.gym_deployment.spec[0].template[0].metadata[0].labels["app"]
    }

    port {
      port        = 80
      target_port = 5000
      protocol    = "TCP"
    }
  }
}
