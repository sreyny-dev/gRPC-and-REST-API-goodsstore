# Use Python 3.10 Alpine as the base image
FROM python:3.10-alpine

# Set the working directory inside the container
WORKDIR /db

# Set environment variables for Flask
ENV FLASK_APP=api_service.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=1680
# Ensure Flask runs on the expected port

# Install dependencies for Python and gRPC compilation
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libc-dev \
    libffi-dev \
    openssl-dev \
    make

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 1680

# Copy the entire application code into the container
COPY . .

# Run the Flask application in production mode
CMD ["flask", "run", "--host=0.0.0.0", "--port=1680"]
