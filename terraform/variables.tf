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

variable "dummy_update" {
  description = "A dummy value that forces an in-place update when changed (e.g., change from \"update30\" to \"update31\")."
  type        = string
  default     = "update31"
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
variable "image_tag" {
  description = "The tag to use for the container image."
  type        = string
  default     = "latest"
}