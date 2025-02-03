terraform {
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
  chart     = "../gym-chart"  # Adjust the path if needed

  # Override values defined in your chart’s values.yaml
  set {
    name  = "replicaCount"
    value = "1"
  }
  set {
    name  = "image.repository"
    value = "nutzkiller/gym"
  }
  set {
    name  = "image.tag"
    value = "latest"
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
  set {
    name  = "configMap.data.DATABASE_URL"
    value = var.DATABASE_URL
  }
  set {
    name  = "secret.stringData.SECRET_KEY"
    value = var.SECRET_KEY
  }

  depends_on = [kubernetes_namespace.gym]
}

# Existing resources to push the Terraform state file to GitHub after apply/destroy remain unchanged
resource "null_resource" "push_to_github_after_apply" {
  provisioner "local-exec" {
    command = <<EOT
      # Install Git if not already installed
      if ! command -v git &> /dev/null; then
        echo "Git not found. Installing..."
        if [ -x "$(command -v apt)" ]; then
          sudo apt update && sudo apt install -y git
        elif [ -x "$(command -v yum)" ]; then
          sudo yum install -y git
        else
          echo "Unsupported package manager. Install Git manually."
          exit 1
        fi
      fi

      git init
      git config --global user.email "yuvalshmuely8@gmail.com"
      git config --global user.name "NutzKiller"
      git remote add origin https://${var.MY_GITHUB_TOKEN}@github.com/NutzKiller/TF.git || true
      git fetch origin main || true
      git checkout -B main || true
      git pull origin main --allow-unrelated-histories --strategy-option ours || true
      git add terraform_state/terraform.tfstate
      git commit -m "Update Terraform state file after apply" || true
      git push origin main --force
    EOT
    environment = {
      MY_GITHUB_TOKEN = var.MY_GITHUB_TOKEN
    }
  }

  triggers = {
    apply_trigger = uuid()
  }
}

resource "null_resource" "push_to_github_after_destroy" {
  provisioner "local-exec" {
    command = <<EOT
      if ! command -v git &> /dev/null; then
        echo "Git not found. Installing..."
        if [ -x "$(command -v apt)" ]; then
          sudo apt update && sudo apt install -y git
        elif [ -x "$(command -v yum)" ]; then
          sudo yum install -y git
        else
          echo "Unsupported package manager. Install Git manually."
          exit 1
        fi
      fi

      git init
      git config --global user.email "yuvalshmuely8@gmail.com"
      git config --global user.name "NutzKiller"
      git remote add origin https://${var.MY_GITHUB_TOKEN}@github.com/NutzKiller/TF.git || true
      git fetch origin main || true
      git checkout -B main || true
      git pull origin main --allow-unrelated-histories --strategy-option ours || true
      git add terraform_state/terraform.tfstate
      git commit -m "Update Terraform state file after destroy" || true
      git push origin main --force
    EOT
    environment = {
      MY_GITHUB_TOKEN = var.MY_GITHUB_TOKEN
    }
  }

  triggers = {
    destroy_trigger = uuid()
  }

  lifecycle {
    create_before_destroy = false
  }
}
