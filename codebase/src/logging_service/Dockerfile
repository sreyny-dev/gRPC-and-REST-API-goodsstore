# Use Python 3.10 slim as the base image
FROM python:3-slim

# Set the working directory inside the container
WORKDIR /logging

# Set environment variables for Flask and Kafka
ENV FLASK_APP=local_publisher.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Install system dependencies for Python, Kafka, and related libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libsasl2-dev \
    libssl-dev \
    make \
    python3-dev \
    librdkafka-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by Flask
EXPOSE 5001

# Copy the entire application code into the container
COPY . .

# Run the Flask application in production mode
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]