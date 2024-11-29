# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /db

# Install build dependencies for your packages
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libffi-dev \
    libssl-dev \
    make \
    linux-libc-dev && \
    rm -rf /var/lib/apt/lists/*  # Clean up the apt cache to reduce image size

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the gRPC port (default is 50051)
EXPOSE 50051

# Command to run the gRPC server
CMD ["python", "local_manager.py"]
