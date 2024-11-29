# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /api

# Install build dependencies and PostgreSQL development libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8081

# Environment variables
ENV FLASK_APP=api_service.py
ENV FLASK_ENV=test

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
