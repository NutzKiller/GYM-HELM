# Use the official Python image as the base
FROM python:3.10-slim

# Prevent Python from writing .pyc files and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# (Optional) Install system dependencies if needed
# Uncomment these lines if your application requires additional packages
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the default command to run the application using Gunicorn.
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]