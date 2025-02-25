# GCP Service Account Credentials JSON File
variable "GCP_CREDENTIALS_FILE" {
  description = "Path to the GCP service account credentials JSON file"
  type        = string
}

# GCP Project ID
variable "GCP_PROJECT" {
  description = "GCP Project ID"
  type        = string
}

# GCP Region
variable "GCP_REGION" {
  description = "GCP Region"
  type        = string
}

# Database Connection String
variable "DATABASE_URL" {
  description = "Database connection string"
  type        = string
}

# Flask Application Secret Key
variable "SECRET_KEY" {
  description = "Flask application secret key"
  type        = string
}

# GitHub Token
variable "MY_GITHUB_TOKEN" {
  description = "GitHub token with permissions to push to the TF repository"
  type        = string
}
variable "dummy_update" {
  description = "A dummy value that, when changed, forces an in-place update of the node pool."
  type        = string
  default     = "update3"
}
