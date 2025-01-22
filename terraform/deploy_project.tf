# Define AWS provider
provider "aws" {
  region = "us-east-1"  # Adjust to your preferred region
}

# Generate a new private key
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Upload the public key to AWS as a key pair
resource "aws_key_pair" "generated_key" {
  key_name   = "generated-key-${random_id.key_id.hex}" # Unique key name with random ID
  public_key = tls_private_key.example.public_key_openssh
}

# Generate a random ID for key uniqueness
resource "random_id" "key_id" {
  byte_length = 4
}

# Use the pre-defined security group "project-security-group"
data "aws_security_group" "project_sg" {
  filter {
    name   = "group-name"
    values = ["project-security-group"]
  }
}

# Launch an EC2 instance
resource "aws_instance" "project_instance" {
  ami           = "ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI
  instance_type = "t2.micro"
  key_name      = aws_key_pair.generated_key.key_name

  security_groups = [data.aws_security_group.project_sg.name]

  # User data script to set up Docker, clone the repository, and run docker-compose
  user_data = <<-EOF
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

              # Run docker-compose
              /usr/local/bin/docker-compose up -d
              EOF

  tags = {
    Name = "GymProject"
  }
}

# Save the private key to a file
resource "local_file" "private_key" {
  content  = tls_private_key.example.private_key_pem
  filename = "generated_key.pem"
}

# Output the public IP address
output "public_ip" {
  value = aws_instance.project_instance.public_ip
}
