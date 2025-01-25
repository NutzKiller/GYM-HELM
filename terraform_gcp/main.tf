############################################
#  terraform_gcp/main.tf
############################################

variable "project_id" {}
variable "region" {
  default = "us-central1"
}
variable "zone" {
  default = "us-central1-a"
}

############################################
# Provider
############################################
provider "google" {
  project     = var.project_id
  region      = var.region
  zone        = var.zone
  credentials = file("${path.module}/gcp-keyfile.json")
}

########################################
# 1) Enable Cloud SQL Admin API
########################################
resource "google_project_service" "enable_sqladmin_052" {
  project = var.project_id
  service = "sqladmin.googleapis.com"

  disable_on_destroy = false
}

########################################
# 2) Use Existing VPC Network + Firewall
########################################

# Reference existing VPC network
data "google_compute_network" "existing_network" {
  name    = "gym-network-053" # Changed network name
  project = var.project_id
}

# Create a new firewall rule for the existing network
resource "google_compute_firewall" "gym_firewall_052" {
  name    = "gym-firewall-052"
  project = var.project_id
  network = data.google_compute_network.existing_network.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "5000"]
  }

  source_ranges = ["0.0.0.0/0"]
}

########################################
# 3) Use Existing Storage Bucket
########################################
data "google_storage_bucket" "existing_exercise_videos" {
  name = "${var.project_id}-exercise-videos-052" # Reference existing bucket
}

########################################
# 4) Use Existing Cloud SQL Instance and Database
########################################

# Reference the existing SQL instance
data "google_sql_database_instance" "existing_gym_sql_instance" {
  name    = "gym-db-instance-052"
  project = var.project_id
}

# Reference the existing database
data "google_sql_database" "existing_gym_database" {
  name     = "GYM"
  instance = data.google_sql_database_instance.existing_gym_sql_instance.name
  project  = var.project_id
}

########################################
# 5) GCE VM for Docker + Your App
########################################
resource "google_compute_instance" "gym_instance_052" {
  name         = "gym-instance-052"
  machine_type = "e2-micro"
  project      = var.project_id
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network       = data.google_compute_network.existing_network.self_link
    access_config {}
  }

  # Improved startup script to handle errors and ensure execution
  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -e

    # Logging setup
    LOGFILE=/var/log/startup-script.log
    exec > >(tee -i ${LOGFILE})
    exec 2>&1

    echo "Startup script started at $(date)"

    # Update packages
    apt-get update -y

    # Install required packages
    apt-get install -y gnupg apt-transport-https ca-certificates curl software-properties-common git

    # Install Docker
    echo "Installing Docker..."
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io

    # Enable and start Docker
    systemctl enable docker
    systemctl start docker

    # Install docker-compose
    echo "Installing Docker-Compose..."
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" \
      -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Clone the GitHub repository
    echo "Cloning the GitHub repository..."
    if [ ! -d "/root/gym" ]; then
      git clone https://github.com/NutzKiller/gym.git /root/gym
    else
      echo "Repository already cloned."
    fi

    # Navigate to the repo and start containers
    cd /root/gym
    echo "Starting Docker containers..."
    docker-compose up -d

    echo "Startup script completed at $(date)"
  EOT

  tags = ["gym-instance"]
}

########################################
# 6) Outputs
########################################
output "instance_external_ip" {
  description = "Public IP of the GCE instance"
  value       = google_compute_instance.gym_instance_052.network_interface[0].access_config[0].nat_ip
}

output "storage_bucket_name" {
  description = "Name of the existing bucket"
  value       = data.google_storage_bucket.existing_exercise_videos.name
}

output "cloudsql_public_ip" {
  description = "Public IP of the existing Cloud SQL instance"
  value       = data.google_sql_database_instance.existing_gym_sql_instance.public_ip_address
}
