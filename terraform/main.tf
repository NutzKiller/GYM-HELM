terraform {
  backend "gcs" {
    bucket = "tfstate_gymproject"
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
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
  }

  required_version = ">= 1.0.0"
}

# Get default Google client configuration (to obtain an access token)
data "google_client_config" "default" {}

provider "google" {
  credentials = file(var.GCP_CREDENTIALS_FILE)
  project     = var.GCP_PROJECT
  region      = var.GCP_REGION
}

provider "kubernetes" {
  host                   = "https://${google_container_cluster.primary.endpoint}"
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
  token                  = data.google_client_config.default.access_token
}

provider "helm" {
  kubernetes {
    host                   = "https://${google_container_cluster.primary.endpoint}"
    cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
    token                  = data.google_client_config.default.access_token
  }
}

# Generate a random ID to make key names unique
resource "random_id" "key_id" {
  byte_length = 4
}

# Generate a new private key
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Save the private key to a file (optional, consider security implications)
resource "local_file" "private_key" {
  content  = tls_private_key.example.private_key_pem
  filename = "generated_key.pem"
}

# Create Kubernetes Namespace for Gym
resource "kubernetes_namespace" "gym" {
  metadata {
    name = "gym-namespace"
  }
}

# Deploy the Helm Chart for Gym
resource "helm_release" "gym" {
  name      = "gym"
  namespace = kubernetes_namespace.gym.metadata[0].name
  chart     = "../gym-chart"  # Adjust if needed

  # Increase timeout and wait for pods to become Ready
  timeout = 720  # 10 minutes
  wait    = true

  # Ensure we only install after the cluster, node pool, and namespace are ready
  depends_on = [
    google_container_cluster.primary,
    google_container_node_pool.primary_nodes,
    kubernetes_namespace.gym
  ]

  # Override values defined in your chart’s values.yaml
  set {
    name  = "replicaCount"
    value = "1"
  }
  # Override the image as a flat string rather than using nested keys.
  set {
    name  = "image"
    value = "nutzkiller/gym:${var.image_tag}"
  }
  set {
    name  = "imagePullPolicy"
    value = "Always"
  }
  set {
    name  = "containerPort"
    value = "5000"
  }
  set {
    name  = "service.type"
    value = "LoadBalancer"
  }
  set {
    name  = "service.port"
    value = "5000"
  }
  # Override flat keys for database URL and secret key
  set {
    name  = "databaseUrl"
    value = var.DATABASE_URL
  }
  set {
    name  = "secretKey"
    value = var.SECRET_KEY
  }
}
