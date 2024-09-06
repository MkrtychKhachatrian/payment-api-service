# Payment API Service

## Overview

This project is a Django-based application for managing loan payments, built with Docker. It provides an API for creating loans, generating payment schedules, and modifying payments.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

Follow these steps to deploy and use the application.

### 1. Clone the Repository

First, clone the repository to your local machine:

```sh
git clone https://github.com/MkrtychKhachatrian/payment-api-service.git
cd payment-api-service
```

### 2. Build and Run the Docker Containers
To build the Docker images and start the containers, run:

```sh
docker-compose up --build
```
This command will:

Build the Docker images defined in the Dockerfile and docker-compose.yml file.
Start the containers as defined in the docker-compose.yml file.


### 3. Apply Migrations
Once the containers are up and running, apply the database migrations:

```sh
docker-compose exec web python manage.py migrate
```


### 4. Run Tests
To ensure everything is working correctly, you can run the tests:


```sh
docker-compose exec web pytest
```


### 5. Access the Application
The application should now be accessible at http://localhost:8000.

#### API Endpoints
- POST /loans/: Create a new loan and generate a payment schedule.
- PATCH /payments/{payment_id}/: Modify an existing payment.
