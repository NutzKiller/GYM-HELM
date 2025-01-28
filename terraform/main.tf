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

# Define Google Cloud provider
provider "google" {
  credentials = file("terraform/gcp_credentials.json") # File created in the GitHub Actions workflow from the secret
  project     = "noted-victory-448912-q2"             # Hardcoded or passed as an environment variable via the workflow
  region      = "us-central1"                         # Hardcoded or passed as an environment variable via the workflow
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
