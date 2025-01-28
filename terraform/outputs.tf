# Terraform outputs

output "kubernetes_cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.primary.name
}

output "kubernetes_cluster_endpoint" {
  description = "Endpoint of the GKE cluster"
  value       = google_container_cluster.primary.endpoint
}

output "kubernetes_cluster_ca_certificate" {
  description = "CA certificate for the GKE cluster"
  value       = google_container_cluster.primary.master_auth.0.cluster_ca_certificate
}

output "public_ip" {
  description = "External IP address of the service"
  value       = kubernetes_service.gym_service.load_balancer_ingress[0].ip
}
