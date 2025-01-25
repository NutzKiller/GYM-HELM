############################################
#  terraform_gcp/main.tf
############################################

# ---------------------------------------------------------
# Inputs - to feed them via variables or environment
# ---------------------------------------------------------
variable "project_id" {}
variable "region" {
  default = "us-central1"
}
variable "zone" {
  default = "us-central1-a"
}

# ---------------------------------------------------------
# Provider
# ---------------------------------------------------------
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone

  # If you store credentials in a JSON file or in GitHub secrets:
  # credentials = file("./path/to/service_account_key.json")
  # Alternatively, you can rely on GOOGLE_CLOUD_KEYFILE_JSON env variable
}

# ---------------------------------------------------------
# Create a network + firewall (allow port 22, 5000, 80, etc.)
# ---------------------------------------------------------
resource "google_compute_network" "gym_network" {
  name = "gym-network"
}

resource "google_compute_firewall" "gym_firewall" {
  name    = "gym-firewall"
  network = google_compute_network.gym_network.name

  allow {
    protocol = "tcp"
    ports    = ["22","80","5000"]
  }

  # 0.0.0.0/0 is wide open, but you said security is not a concern for your project
  source_ranges = ["0.0.0.0/0"]
}

# ---------------------------------------------------------
# (Optional) Create a Google Cloud Storage bucket for videos
# For future usage, if you want to host static videos cheaply
# ---------------------------------------------------------
resource "google_storage_bucket" "exercise_videos" {
  name          = "${var.project_id}-exercise-videos"
  location      = var.region
  force_destroy = true
  # For public read access (not recommended in real production)
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
  uniform_bucket_level_access = false
}

# ---------------------------------------------------------
# Create a VM instance that runs Docker + your app
# ---------------------------------------------------------
resource "google_compute_instance" "gym_instance" {
  name         = "gym-instance"
  machine_type = "e2-micro"
  zone         = var.zone

  # Ubuntu or Debian family - up to you
  # Check https://cloud.google.com/compute/docs/images
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11" # Debian 11
    }
  }

  network_interface {
    network = google_compute_network.gym_network.self_link
    access_config {
      # Ephemeral public IP
    }
  }

  # If you want to use an SSH key, see google_compute_project_metadata. 
  # For simplicity, we skip that.

  # Startup script: install Docker, git clone your repo, run docker-compose up
  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update -y
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common git

    # Install Docker
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io

    systemctl enable docker
    systemctl start docker

    # Install docker-compose (latest stable)
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" \
      -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Clone your GitHub repo
    cd /root
    git clone https://github.com/NutzKiller/gym.git
    cd gym

    # Run docker-compose
    docker-compose up -d
  EOT

  tags = ["gym-instance"]
}

# ---------------------------------------------------------
# Outputs
# ---------------------------------------------------------
output "instance_external_ip" {
  description = "The public IP of the GCE instance"
  value       = google_compute_instance.gym_instance.network_interface[0].access_config[0].nat_ip
}

output "storage_bucket_name" {
  description = "Name of the optional bucket for videos"
  value       = google_storage_bucket.exercise_videos.name
}
