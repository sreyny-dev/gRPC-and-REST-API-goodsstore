# SUSTech Merch Store - Assignment 2

## CS328 - Distributed and Cloud Computing

### Deadline: 23:59, December 1, 2024

---

## Project Overview

This project involves the development of an online SUSTech Merch Store, where exactly 3 products are available for sale. The store is accessible via a RESTful API Service, which interacts with gRPC microservices for database operations and logging. The system is designed to handle user registration, product browsing, and order placement, with all data stored in a PostgreSQL database. The project also includes a centralized logging service using Kafka for monitoring purposes.

---

## Architecture

The system architecture consists of the following components:

![Architecture Diagram](/img/archi.png)

1. **RESTful API Service**: Handles external customer requests, including product browsing, user management, and order placement.
2. **gRPC DB Service**: Manages database operations, including CRUD operations for products, users, and orders. It maintains a connection pool to optimize database access.
3. **gRPC Logging Service**: Collects logs from the API and DB services and publishes them to a Kafka topic for monitoring.
4. **PostgreSQL Database**: Stores product, user, and order information.
5. **Kafka**: Used for centralized logging and monitoring.

All components are deployed using Docker Compose.

---

## Tasks

### 1. API Service
- Implement the following APIs:
  - **Greeting API**: Returns a welcome message.
  - **Product APIs**: `list-products`, `get-product`.
  - **User APIs**: `register`, `deactivate-user`, `get-user`, `update-user`, `login`.
  - **Order APIs**: `place-order`, `cancel-order`, `get-order`.
- Define the APIs in an OpenAPI specification YAML file.
- Implement JWT-based authentication for user-specific APIs.

### 2. DB Service
- Implement CRUD operations for products, users, and orders.
- Define the RPCs in a Proto file.

### 3. Logging Service
- Implement a client-side streaming RPC to collect log messages.
- Define the RPCs in a Proto file.

### 4. Docker Compose
- Update the provided Docker Compose file to include all services and ensure they can communicate with each other.

---

## Requirements

1. **API/RPC Definitions**: Ensure reasonable API/RPC definitions (e.g., `get-user` should not return sensitive information like passwords).
2. **Authentication**: Implement JWT-based authentication for user-specific APIs.
3. **Data Types**: Ensure consistent field data types across the OpenAPI specification, Proto files, and database schema.
4. **Error Handling**: Implement gRPC error handling with appropriate status codes and detail messages.
5. **Code Style**: Adhere to standard style guidelines and include comments where necessary.

---

## Report

The report should answer the following questions:

1. **Implementation Procedures**: Explain the setup, code generation, and business logic implementation for each component.
2. **Authentication**: Identify which APIs require authentication and describe the authentication logic.
3. **Data Types**: Explain how you selected field data types for different definitions.
4. **Protobuf Encoding**: Analyze how a Proto message is encoded into binary format and verify the result programmatically.
5. **Logging Service**: Explain how the server-side streaming RPC works.
6. **Docker Configuration**: Describe how Docker and Docker Compose are configured to enable communication between services.
7. **Testing**: Explain how you tested the API Service (e.g., using cURL, Postman, Swagger UI) and monitored log messages from the Kafka topic.
