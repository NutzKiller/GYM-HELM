#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Update the system
apt update -y

# Install Docker
amazon-linux-extras enable docker
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install Git
apt install -y git

# Clone the repository
if [ ! -d "/home/ec2-user/gym" ]; then
    git clone https://github.com/NutzKiller/gym.git /home/ec2-user/gym
fi
cd /home/ec2-user/gym

# Install Docker Compose
if [ ! -f "/usr/local/bin/docker-compose" ]; then
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Set environment variables from Terraform
echo "DATABASE_URL=${database_url}" >> /etc/environment
echo "SECRET_KEY=${secret_key}" >> /etc/environment
export DATABASE_URL=${database_url}
export SECRET_KEY=${secret_key}

# Run Docker Compose from the cloned repository
/usr/local/bin/docker-compose up -d
