# Push the Terraform state file to GitHub after apply or destroy

resource "null_resource" "push_to_github_after_apply" {
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

      # Add GitHub remote with token-based authentication
      git remote add origin https://${var.MY_GITHUB_TOKEN}@github.com/NutzKiller/TF.git || true

      # Ensure branch exists and check it out
      git fetch origin main || true
      git checkout -B main || true

      # Pull the latest changes and resolve conflicts by overwriting with local changes
      git pull origin main --allow-unrelated-histories --strategy-option ours || true

      # Add and commit the Terraform state file
      git add terraform_state/terraform.tfstate
      git commit -m "Update Terraform state file after apply" || true

      # Force push to GitHub
      git push origin main --force
    EOT
    environment = {
      MY_GITHUB_TOKEN = var.MY_GITHUB_TOKEN
    }
  }

  triggers = {
    apply_trigger = uuid()
  }
}

resource "null_resource" "push_to_github_after_destroy" {
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

      # Add GitHub remote with token-based authentication
      git remote add origin https://${var.MY_GITHUB_TOKEN}@github.com/NutzKiller/TF.git || true

      # Ensure branch exists and check it out
      git fetch origin main || true
      git checkout -B main || true

      # Pull the latest changes and resolve conflicts by overwriting with local changes
      git pull origin main --allow-unrelated-histories --strategy-option ours || true

      # Add and commit the Terraform state file
      git add terraform_state/terraform.tfstate
      git commit -m "Update Terraform state file after destroy" || true

      # Force push to GitHub
      git push origin main --force
    EOT
    environment = {
      MY_GITHUB_TOKEN = var.MY_GITHUB_TOKEN
    }
  }

  triggers = {
    destroy_trigger = uuid()
  }

  lifecycle {
    create_before_destroy = false
  }
}
