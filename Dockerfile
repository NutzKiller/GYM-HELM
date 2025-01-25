# Use the official Python image as the base
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and to ensure stdout and stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any are required)
# Uncomment and modify the following lines if your application requires additional system packages
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file to the container
COPY requirements.txt /app/

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary application files to the container
COPY app.py /app/
COPY templates /app/templates
COPY static /app/static

# (Optional) If you have additional modules or packages, copy them as well
# COPY your_module/ /app/your_module/

# Expose port 5000 to allow external access to the Flask app
EXPOSE 5000

# Define the default command to run the Flask app
CMD ["python", "app.py"]
