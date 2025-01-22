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
  key_name   = "generated-key-from-terraform"
  public_key = tls_private_key.example.public_key_openssh
}

# Create a security group to allow HTTP and SSH traffic
resource "aws_security_group" "project_sg_2" {
  name        = "project-security-group"
  description = "Allow HTTP and SSH traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Launch an EC2 instance
resource "aws_instance" "project_instance" {
  ami           = "ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI
  instance_type = "t2.micro"
  key_name      = aws_key_pair.generated_key.key_name

  security_groups = [aws_security_group.project_sg.name]

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