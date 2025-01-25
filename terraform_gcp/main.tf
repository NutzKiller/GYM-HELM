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
resource "google_project_service" "enable_sqladmin_055" {
  project = var.project_id
  service = "sqladmin.googleapis.com"

  disable_on_destroy = false
}

########################################
# 2) Use Existing VPC Network
########################################
data "google_compute_network" "existing_network" {
  name    = "gym-network-052" # Use the existing VPC name
  project = var.project_id
}

# Reference existing firewall by name instead of creating a data block
resource "google_compute_firewall" "gym_firewall_055" {
  name    = "gym-firewall-055" # Creating a new firewall if needed
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
  name = "${var.project_id}-exercise-videos-052" # Ensure to use the existing bucket name
}

########################################
# 4) Cloud SQL Instance (Use Existing)
########################################

data "google_sql_database_instance" "existing_gym_sql_instance" {
  name    = "gym-db-instance-052" # Use the existing SQL instance name
  project = var.project_id
}

data "google_sql_database" "existing_gym_database" {
  name     = "GYM" # Use the existing database name
  instance = data.google_sql_database_instance.existing_gym_sql_instance.name
  project  = var.project_id
}

########################################
# 5) GCE VM for Docker + Your App
########################################
resource "google_compute_instance" "gym_instance_055" {
  name         = "gym-instance-055" # Creating a new VM with a unique name
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

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update -y
    apt-get install -y gnupg apt-transport-https ca-certificates curl software-properties-common git

    # Install Docker
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io

    systemctl enable docker
    systemctl start docker

    # Install docker-compose
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" \
      -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Clone your GitHub repo
    cd /root
    git clone https://github.com/NutzKiller/gym.git
    cd gym

    # Up the containers
    docker-compose up -d
  EOT

  tags = ["gym-instance"]
}

########################################
# 6) Outputs
########################################
output "instance_external_ip" {
  description = "Public IP of the GCE instance"
  value       = google_compute_instance.gym_instance_055.network_interface[0].access_config[0].nat_ip
}

output "storage_bucket_name" {
  description = "Name of the existing bucket"
  value       = data.google_storage_bucket.existing_exercise_videos.name
}

output "cloudsql_public_ip" {
  description = "Public IP of the existing Cloud SQL instance"
  value       = data.google_sql_database_instance.existing_gym_sql_instance.public_ip_address
}
