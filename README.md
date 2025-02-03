# Gym Workout Plan Generator

Welcome to the **Gym Workout Plan Generator**! This web application is designed to generate a weekly workout plan for gym-goers, with workouts for various muscle groups including chest, shoulders, triceps, back, biceps, and legs. It provides users with a personalized workout plan each week, selecting exercises from a database.

## Features

- **Generate Weekly Workouts**: Automatically generates 6 different workouts each week, targeting specific muscle groups.
  - **Workout A**: Chest, Shoulders, Triceps (3 chest exercises, 2 shoulder exercises, 2 tricep exercises).
  - **Workout B**: Back, Biceps (4 back exercises, 3 bicep exercises).
  - **Workout C**: Legs (5 leg exercises).
- **Personalized Routine**: Customize your workout plan based on specific needs and goals.
- **Exercise Database**: Access a curated collection of exercises for each muscle group.

## Technologies Used

- **Flask**: A lightweight Python web framework for building the backend.
- **Docker**: Containerization for ease of deployment and consistent environments.
- **Python**: The primary language for implementing the workout logic.
- **Terraform & Helm**: Infrastructure as Code (IaC) tools used to provision a GKE cluster and deploy the application.
- **Google Cloud Platform (GCP)**: Hosting the Kubernetes cluster on GKE.
- **HTML/CSS & Bootstrap**: Front-end development for a responsive user interface.

## Installation & Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/NutzKiller/gym.git
cd gym
