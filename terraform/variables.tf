# Terraform variables

variable "GCP_CREDENTIALS_FILE" {
  description = "Path to the GCP credentials JSON file"
  type        = string
}

variable "GCP_PROJECT" {
  description = "GCP project ID"
  type        = string
}

variable "GCP_REGION" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "DATABASE_URL" {
  description = "The database connection string"
  type        = string
}

variable "SECRET_KEY" {
  description = "The Flask application secret key"
  type        = string
}

variable "MY_GITHUB_TOKEN" {
  description = "GitHub token for pushing Terraform state"
  type        = string
  sensitive   = true
}
