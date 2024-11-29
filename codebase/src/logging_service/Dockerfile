FROM python:3.10-slim

# Set working directory
WORKDIR /logging

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

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the gRPC port (default is 50051)
EXPOSE 50052

# Command to run the gRPC server
CMD ["python", "local_publisher.py"]