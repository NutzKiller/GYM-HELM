# Gym Workout Web App

A modern, containerized web application built with Python Flask that empowers trainers and trainees to explore pre-built gym workouts or create custom workout plans. Each exercise in the library includes instructional videos hosted in a Google Cloud bucket, and all workout data, user profiles, and video URLs are securely stored in a Google Cloud SQL database.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Architecture & Tooling](#project-architecture--tooling)
- [CI/CD Pipeline Flow](#cicd-pipeline-flow)
- [Setup Instructions](#setup-instructions)
  - [Local Development](#local-development)
  - [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [GitHub Secrets & Variables](#github-secrets--variables)
- [Additional Information](#additional-information)
  - [Docker](#docker)
  - [Infrastructure as Code](#infrastructure-as-code)
  - [Observability](#observability)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project is a Python Flask-based web application that allows users to:

- **Explore Workout Plans:** Access pre-built gym workouts or create custom plans.
- **Watch Exercise Videos:** View instructional videos demonstrating proper exercise techniques and muscle targeting.
- **Manage User Data:** Securely store and manage personalized workout plans and profiles using a Google Cloud SQL database.

The application is fully containerized using Docker and employs a comprehensive CI/CD pipeline orchestrated through GitHub Actions. Deployments are automated with Terraform, Helm, ArgoCD, and Kubernetes on Google Cloud, ensuring a reliable, scalable, and well-monitored production environment.

---

## Features

- **Flask Web Application:** A lightweight yet robust Python web app.
- **Dynamic Content:** Displays updated workout and exercise video data on every refresh.
- **User Management:** Securely handles user profiles and workout plans.
- **Cloud Storage:** Videos are stored in a Google Cloud bucket, with corresponding URLs saved in the database.
- **Containerization:** Docker ensures consistent runtime environments.
- **CI/CD Automation:** GitHub Actions automatically builds, tests, and deploys the application.
- **Infrastructure as Code:** Terraform provisions the Kubernetes cluster on Google Cloud.
- **Kubernetes & Helm:** Manage container orchestration and application deployments.
- **Observability:** Integrated monitoring and logging via Prometheus, Grafana, and Loki.
- **GitOps Deployment:** ArgoCD automates continuous deployment updates.

---

## Project Architecture & Tooling

### Application Components

- **Python Flask:** The core framework powering the web application.
- **Docker:** Containerizes the application, encapsulating all dependencies and configurations.
- **Git & GitHub:** Facilitates source code management and collaboration.
- **Google Cloud SQL:** Hosts the database for user data and workout plans.
- **Google Cloud Bucket:** Stores the exercise video files.

### DevOps & Deployment Tools

- **Terraform:** Automates infrastructure provisioning on Google Cloud by creating and managing a Kubernetes cluster.
- **Helm:** Packages Kubernetes manifests to simplify deployments and manage updates.
- **ArgoCD:** Implements GitOps principles for continuous delivery.
- **Kubernetes (k8s):** Orchestrates container deployments ensuring scalability and high availability.
- **GitHub Actions:** Automates the CI/CD pipeline by building Docker images, running tests, and deploying updates.
- **Prometheus, Grafana & Loki:** Provide real-time monitoring, metrics visualization, and log aggregation.

---

## CI/CD Pipeline Flow

1. **Code Push & Pipeline Trigger**  
   Every code commit triggers GitHub Actions, initiating the CI/CD pipeline.

![CI/CD Pipeline](assets/diagram.png)

2. **Continuous Integration (CI)**
   - **Docker Build:** The application is built into a Docker image.
   - **Image Push:** The Docker image is pushed to the designated container registry.
   - **Helm Packaging:** Helm charts are updated with the new image tag and packaged.
   - **Testing:** Automated tests run using Docker Compose to ensure functionality.

3. **Continuous Deployment (CD)**
   - **Terraform Deployment:** Infrastructure is provisioned or updated on Google Cloud (Kubernetes cluster).
   - **ArgoCD Deployment:** ArgoCD deploys or updates the application using the latest Helm chart.
   - **Monitoring Tools:** Once deployed, Prometheus, Grafana, and Loki provide real-time insights into performance and logs.

---

## Setup Instructions

### Local Development

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/your-gym-workout-app.git
   cd your-gym-workout-app

    Environment Variables: Create a .env file (or configure your local environment) with the necessary secrets:
        DATABASE_URL
        DOCKER_USERNAME
        DOCKER_PASSWORD
        GCP_CREDENTIALS_FILE_B64
        GCP_CREDENTIALS_JSON
        GCP_PROJECT
        GCP_REGION
        MY_GITHUB_TOKEN
        SECRET_KEY

    Build & Run Locally:

    docker build -t gym-workout-app .
    docker run -p 5000:5000 gym-workout-app

    Verify the app is running by visiting http://localhost:5000.

Deployment

    Push Changes: When you push new code, GitHub Actions automatically builds, tests, and pushes the Docker image.

    Infrastructure Provisioning: Use Terraform to set up or update your Google Cloud Kubernetes cluster:

    terraform init
    terraform apply

    Deploy via ArgoCD: ArgoCD detects changes and deploys the latest Helm chart to your cluster. Ensure the Helm charts are updated with the new Docker image tag.

    Monitoring & Logging: Once deployed, the integrated monitoring stack (Prometheus, Grafana, Loki) will provide real-time insights into application performance and logs.

Environment Variables

Create a .env file (or configure your local environment) with the following secrets:

    DATABASE_URL
    DOCKER_USERNAME
    DOCKER_PASSWORD
    GCP_CREDENTIALS_FILE_B64
    GCP_CREDENTIALS_JSON
    GCP_PROJECT
    GCP_REGION
    MY_GITHUB_TOKEN
    SECRET_KEY

GitHub Secrets & Variables

To secure the CI/CD process, configure the following GitHub secrets in your repository settings:

    DATABASE_URL
    DOCKER_USERNAME
    DOCKER_PASSWORD
    GCP_CREDENTIALS_FILE_B64
    GCP_CREDENTIALS_JSON
    GCP_PROJECT
    GCP_REGION
    MY_GITHUB_TOKEN
    SECRET_KEY

Note: Each secret has an associated update date to track recent changes.
Additional Information
Docker

    Dockerfile:
    Defines how the Flask app is packaged into a container.

    Docker Compose (Optional):
    Use Docker Compose for local multi-container testing:

    docker compose up --build

Infrastructure as Code

    Terraform:
    Provisions and manages the Google Cloud Kubernetes cluster, ensuring that infrastructure is version-controlled and reproducible.

    Helm:
    Simplifies deployments by packaging Kubernetes manifests and allowing easy updates or rollbacks.

Observability

    Prometheus:
    Collects key metrics from the application.

    Grafana:
    Provides dashboards for visualizing metrics.

    Loki:
    Aggregates and stores logs for efficient troubleshooting.

Contributing

Contributions are welcome! Please follow these guidelines:

    Fork the repository and create your feature branch.
    Ensure new code includes tests.
    Submit a pull request with detailed explanations of your changes.
