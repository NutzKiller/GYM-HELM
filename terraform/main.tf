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
  credentials = file(var.GCP_CREDENTIALS_FILE) # Uses the file created from the GitHub secret
  project     = var.GCP_PROJECT               # Passed as a variable from the workflow
  region      = var.GCP_REGION
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
