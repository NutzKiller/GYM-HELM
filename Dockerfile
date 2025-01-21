# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY app.py /app/

# Copy the JSON files
COPY exercises.json /app/
COPY products.json /app/
COPY users.json /app/

# Copy the templates directory
COPY templates /app/templates

# Copy the static files
COPY static /app/static

# Expose the port your Flask app listens on
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
