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
# 2) Create or Reuse VPC Network + Firewall
########################################

# Try to find the existing network
data "google_compute_network" "existing_network" {
  name    = "gym-network-053"
  project = var.project_id
  depends_on = [google_project_service.enable_sqladmin_052]
  # Will fail gracefully if it doesn't exist, allowing the resource below to create it.
}

# Create the network if it doesn't exist
resource "google_compute_network" "new_network" {
  count = length(try(data.google_compute_network.existing_network.id, [])) == 0 ? 1 : 0
  name  = "gym-network-053"
  auto_create_subnetworks = true
  project = var.project_id
}

# Create the firewall rule
resource "google_compute_firewall" "gym_firewall_052" {
  name    = "gym-firewall-052"
  project = var.project_id
  network = coalesce(data.google_compute_network.existing_network.self_link, google_compute_network.new_network[0].self_link)

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "5000"]
  }

  source_ranges = ["0.0.0.0/0"]
}

########################################
# 3) Use Existing or Create Storage Bucket
########################################
data "google_storage_bucket" "existing_exercise_videos" {
  name = "${var.project_id}-exercise-videos-052"
}

resource "google_storage_bucket" "exercise_videos_052" {
  count = length(try(data.google_storage_bucket.existing_exercise_videos.id, [])) == 0 ? 1 : 0
  name  = "${var.project_id}-exercise-videos-052"
  location = var.region
  force_destroy = true
  uniform_bucket_level_access = false

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
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
    network       = coalesce(data.google_compute_network.existing_network.self_link, google_compute_network.new_network[0].self_link)
    access_config {}
  }

  # Startup script to install Docker, clone your repo, run docker-compose
  metadata_startup_script = <<-EOT
    #!/bin/bash
    exec > >(tee /var/log/startup-script.log) 2>&1
    set -e

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

    # Clone your GitHub repo and run docker-compose
    if [ ! -d "/root/gym" ]; then
      cd /root
      git clone https://github.com/NutzKiller/gym.git
    fi
    cd /root/gym

    docker-compose down || true
    docker-compose pull
    docker-compose up -d
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
  description = "Name of the storage bucket"
  value       = coalesce(data.google_storage_bucket.existing_exercise_videos.name, google_storage_bucket.exercise_videos_052[0].name)
}

output "cloudsql_public_ip" {
  description = "Public IP of the Cloud SQL instance"
  value       = data.google_sql_database_instance.existing_gym_sql_instance.public_ip_address
}
