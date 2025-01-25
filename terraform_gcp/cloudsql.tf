# Make sure we enable the API before creating an instance
resource "google_sql_database_instance" "gym_sql" {
  depends_on = [google_project_service.enable_sqladmin]

  name             = "gym-db-instance"
  project          = var.project_id
  region           = var.region
  database_version = "MYSQL_8_0"

  # For a cheap tier:
  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled = true
    }
  }

  # Keep the instance if you destroy:
  deletion_protection = true
}

resource "google_sql_database" "gym_db" {
  depends_on = [google_sql_database_instance.gym_sql]
  name     = "GYM"
  instance = google_sql_database_instance.gym_sql.name
  project  = var.project_id
}

resource "google_sql_user" "app_user" {
  depends_on = [google_sql_database_instance.gym_sql]
  name     = "postgres"
  instance = google_sql_database_instance.gym_sql.name
  host     = "%"
  password = "password"
  project  = var.project_id
}

output "cloudsql_public_ip" {
  value = google_sql_database_instance.gym_sql.public_ip_address
}
