# Configure Terraform backend to store the state locally
terraform {
  backend "local" {
    path = "terraform_state/terraform.tfstate"
  }

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
  }

  required_version = ">= 1.0.0"
}

# Define Google Cloud provider using environment variables directly
provider "google" {
  credentials = file("gcp_credentials.json") # Created in GitHub Actions
  project     = "${var.GCP_PROJECT}"                  # Passed from GitHub Actions as an environment variable
  region      = "${var.GCP_REGION}"                   # Passed from GitHub Actions as an environment variable
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

