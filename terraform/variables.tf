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
variable "node_image_type" {
  description = "The OS image type for the node pool. Change this value (e.g., from COS_CONTAINERD to UBUNTU_CONTAINERD) to force an in-place update."
  type        = string
  default     = "COS_CONTAINERD"
}

variable "max_surge" {
  description = "Max surge for node pool upgrade settings. Change this value to force an in-place update."
  type        = number
  default     = 1
}

variable "max_unavailable" {
  description = "Max unavailable for node pool upgrade settings."
  type        = number
  default     = 0
}
