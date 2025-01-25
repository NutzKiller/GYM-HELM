########################################################
# terraform_gcp/cloudsql.tf
########################################################

resource "google_sql_database_instance" "gym_sql" {
  name             = "gym-db-instance"
  project          = var.project_id
  region           = var.region
  database_version = "MYSQL_8_0"

  settings {
    tier = "db-f1-micro"  # cheap, minimal tier
    ip_configuration {
      ipv4_enabled = true
      # optionally, you can allow only your GCE VM's IP if you want
      # authorized_networks {
      #   name  = "my-gce-vm"
      #   value = "VM_EXTERNAL_IP/32"
      # }
    }
  }
}

# Create the actual "GYM" database
resource "google_sql_database" "gym_db" {
  name     = "GYM"
  instance = google_sql_database_instance.gym_sql.name
  project  = var.project_id
}

# Create a user for your app
resource "google_sql_user" "app_user" {
  name     = "postgres"
  instance = google_sql_database_instance.gym_sql.name
  host     = "%"
  password = "password"
  project  = var.project_id
}

# Optionally, output the public IP so you can see it easily
output "cloudsql_public_ip" {
  description = "Public IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.gym_sql.public_ip_address
}
