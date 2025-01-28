# terraform/variables.tf

variable "GCP_CREDENTIALS_FILE" {
  description = "Path to the GCP service account credentials JSON file"
  type        = string
}

variable "GCP_PROJECT" {
  description = "GCP Project ID"
  type        = string
}

variable "GCP_REGION" {
  description = "GCP Region"
  type        = string
}

variable "DATABASE_URL" {
  description = "Database connection string"
  type        = string
}

variable "SECRET_KEY" {
  description = "Flask application secret key"
  type        = string
}

variable "MY_GITHUB_TOKEN" {
  description = "GitHub token with permissions to push to the TF repository"
  type        = string
}
