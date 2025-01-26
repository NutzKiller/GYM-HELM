#!/bin/bash
yum update -y

# Install Docker
amazon-linux-extras enable docker
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install Git
yum install -y git

# Clone the repository
git clone https://github.com/NutzKiller/gym.git /home/ec2-user/gym
cd /home/ec2-user/gym

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Set environment variables from Terraform
echo "DATABASE_URL=${database_url}" >> /etc/environment
echo "SECRET_KEY=${secret_key}" >> /etc/environment
source /etc/environment

# Run Docker Compose
/usr/local/bin/docker-compose up -d
