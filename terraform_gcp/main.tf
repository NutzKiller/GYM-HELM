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
# 2) New VPC Network + Firewall
########################################
# We'll suffix with -052 so we don't conflict with any older resources
resource "google_compute_network" "gym_network_052" {
  name    = "gym-network-052"
  project = var.project_id
}

resource "google_compute_firewall" "gym_firewall_052" {
  name    = "gym-firewall-052"
  project = var.project_id
  network = google_compute_network.gym_network_052.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "5000"]
  }

  source_ranges = ["0.0.0.0/0"]
}

########################################
# 3) New Bucket
########################################
resource "google_storage_bucket" "exercise_videos_052" {
  # Add '-052' so it's unique
  name          = "${var.project_id}-exercise-videos-052"
  location      = var.region
  force_destroy = true
  uniform_bucket_level_access = false

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}

########################################
# 4) Cloud SQL MySQL instance
########################################
resource "google_sql_database_instance" "gym_sql_052" {
  depends_on = [google_project_service.enable_sqladmin_052]

  name             = "gym-db-instance-052"
  project          = var.project_id
  region           = var.region
  database_version = "MYSQL_8_0"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled = true
    }
  }

  # Protect DB from accidental destroy
  deletion_protection = true
}

# Create the "GYM" database inside that instance
resource "google_sql_database" "gym_db_052" {
  depends_on = [google_sql_database_instance.gym_sql_052]

  name     = "GYM"
  instance = google_sql_database_instance.gym_sql_052.name
  project  = var.project_id
}

# Create a MySQL user named "postgres" with password "password"
resource "google_sql_user" "app_user_052" {
  depends_on = [google_sql_database_instance.gym_sql_052]

  name     = "postgres"
  instance = google_sql_database_instance.gym_sql_052.name
  host     = "%"
  password = "password"
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
    # link to the new "gym-network-052"
    network       = google_compute_network.gym_network_052.self_link
    access_config {}
  }

  # Startup script to install Docker, clone your repo, run docker-compose
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
  description = "Public IP of the new GCE instance"
  value       = google_compute_instance.gym_instance_052.network_interface[0].access_config[0].nat_ip
}

output "storage_bucket_name" {
  description = "Name of the new bucket"
  value       = google_storage_bucket.exercise_videos_052.name
}

output "cloudsql_public_ip" {
  description = "Public IP of the new Cloud SQL instance"
  value       = google_sql_database_instance.gym_sql_052.public_ip_address
}

