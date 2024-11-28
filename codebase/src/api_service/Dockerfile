# Use Python 3.10 Alpine as the base image
FROM python:3.10-alpine

# Set the working directory inside the container
WORKDIR /api

# Set environment variables for Flask
ENV FLASK_APP=api_service.py
ENV FLASK_RUN_HOST=0.0.0.0

# Install dependencies for Python and gRPC compilation
RUN apk add --no-cache gcc musl-dev linux-headers

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 8081 for the Flask application
EXPOSE 8081

# Copy the entire application code into the container
COPY . .

# Run the Flask application in debug mode
CMD ["flask", "run", "--debug"]
