# Configure Terraform backend to store the state locally
terraform {
  backend "local" {
    path = "terraform_state/terraform.tfstate"
  }
}

# Define AWS provider
provider "aws" {
  region = "us-east-1"
}

# Generate a random ID to make key names unique
resource "random_id" "key_id" {
  byte_length = 4
}

# Generate a new private key
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Upload the public key to AWS as a key pair
resource "aws_key_pair" "generated_key" {
  key_name   = "generated-key-${random_id.key_id.hex}"
  public_key = tls_private_key.example.public_key_openssh
}

# Use the pre-defined security group "project-security-group"
data "aws_security_group" "project_sg" {
  filter {
    name   = "group-name"
    values = ["project-security-group"]
  }
}

# Launch an EC2 instance to run the web app
resource "aws_instance" "project_instance" {
  ami           = "ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI
  instance_type = "t2.micro"
  key_name      = aws_key_pair.generated_key.key_name

  security_groups = [data.aws_security_group.project_sg.name]

  # Pass variables into user data
  user_data = templatefile("${path.module}/user_data.sh", {
    database_url = var.DATABASE_URL
    secret_key   = var.SECRET_KEY
  })

  tags = {
    Name = "GymProject"
  }
}

# Save the private key to a file
resource "local_file" "private_key" {
  content  = tls_private_key.example.private_key_pem
  filename = "generated_key.pem"
}

# Push the Terraform state file to GitHub after `terraform apply`
resource "null_resource" "push_to_github" {
  provisioner "local-exec" {
    command = <<EOT
      # Install Git if not already installed
      if ! command -v git &> /dev/null; then
        echo "Git not found. Installing..."
        if [ -x "$(command -v apt)" ]; then
          sudo apt update && sudo apt install -y git
        elif [ -x "$(command -v yum)" ]; then
          sudo yum install -y git
        else
          echo "Unsupported package manager. Install Git manually."
          exit 1
        fi
      fi

      # Ensure Git is initialized
      git init

      # Configure Git user identity
      git config --global user.email "yuvalshmuely8@gmail.com"
      git config --global user.name "NutzKiller"

      # Add GitHub remote
      git remote add origin https://github.com/NutzKiller/TF.git || true

      # Switch to the main branch
      git checkout main || git checkout -b main

      # Add and commit the Terraform state file
      git add terraform_state/terraform.tfstate
      git commit -m "Update Terraform state file"

      # Push to GitHub
      git push -u origin main
    EOT
  }

  # Trigger this resource after the EC2 instance is created
  triggers = {
    instance_id = aws_instance.project_instance.id
  }
}

# Output the public IP address
output "public_ip" {
  value = aws_instance.project_instance.public_ip
}

# Declare Terraform variables for secrets
variable "DATABASE_URL" {
  description = "The database connection string"
  type        = string
}

variable "SECRET_KEY" {
  description = "The Flask application secret key"
  type        = string
}
