# Ipswich Retail E-commerce Application

The following project is an e-commerce platform built using the Django framework with a Model-View-Template (MVT) architecture. which replaces a monolithic architecture in order to improve scalability, reliability, and deployment efficiency. The following application includes core features such as product management, user authentication, shopping cart functionality, and order processing.


## Features

- **Product Management**: Add, update, and display products.
- **User Authentication**: User registration, login, and profile management.
- **Shopping Cart**: Add/remove products and view cart contents.
- **Order Management**: Process and track user orders.
- **Scalable Deployment**: Uses Docker and Render for deployment and monitoring.
- **CI/CD**: Automated build and deployment with Docker and Render.

## Tech stack

- **Backend Framework**: Django (Python)
- **Frontend**: Django Templates (HTML, CSS - using tailwind)
- **Database**: SQLite
- **Containerization**: Docker
- **Deployment & Monitoring**: Render
- **CI/CD**: GitHub Actions (Docker) as well as with Render

## Prerequisites

Kindly not and ensure you have the following installed on your machine:

- Python 3.9 or later
- pip (Python package manager)
- Docker (for containerized development and deployment)
- Git (for version control)
- NodeJS 18x or later

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/asifprog/ecommerce.git
cd ecommerce
```

### 2. Use the provided file **command.sh**
```bash
./command.sh
```

### 3. Then activate the virtual environment
```bash
source env/bin/activate
```

### 4. Run the development server
```bash
python manage.py runserver
```
Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Or

### 2. Set up virtual environment
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```
Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## To work with tailwind in the development enviroment

### 1. open a new terminal tab
```bash
cd theme/static_src
yarn or npm install
yarn or npm start # To start the tailwind server in development mode
```

## Deployment on render
Please note ensure that you have registered render account and linked to your github account

### 1. Create a Render Web Service
- Sign in to [Render](https://render.com/).
- Create a new Web Service and link your GitHub repository.
- Select "Docker" as the environment and configure the service to use the repository's `Dockerfile`.

### 2. Add Environment Variables
- Configure any environment variables (e.g., `DEBUG`, `DATABASE_URL`) in the Render dashboard.
```env
DJANGO_SECRET_KEY='xxxxxx'
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database settings in case of change to a different database
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# unsplash
UNSPLASH_ACCESS_KEY='xxxxx'

### 3. Automatic deployments
- Render will automatically build and deploy the application on every push to the `main` branch using the linked GitHub repository.

## Docker for CI/CD

### Docker workflow
Render uses Docker to build and deploy the application automatically. The following Docker configuration ensures seamless CI/CD integration:

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

RUN node -v && npm -v

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# COPY .env .env

COPY theme/static_src/package.json theme/static_src/package-lock.json ./theme/static_src/

WORKDIR /app/theme/static_src
RUN npm install -g yarn && yarn install

WORKDIR /app
COPY . .

RUN python manage.py makemigrations
RUN python manage.py migrate

RUN python manage.py generate_products
RUN python manage.py seed_products


RUN python manage.py tailwind build

RUN python manage.py collectstatic

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=ecommerce.settings
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ecommerce.wsgi:application"]
```

### Using render to handles CI/CD
Below are some of the steps followed
- Render automatically builds the Docker image specified in the `Dockerfile`.
- Once the image is built, Render deploys the containerized application and starts the services.
- No separate CI/CD configurations are needed outside the Dockerfile and Render's native setup.

### Using github action
The following code below is used to run the action for the **Dockerfile** on push to test the

```yml
name: Docker Image CI

on:
  push:
    branches: 
      - "master"
  pull_request:
    branches: 
      - "master"

jobs:

  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Build the Docker image
      run: docker build . --file Dockerfile --tag my-image-name:$(date +%s)
```

## Monitoring with Render
Render provides built-in monitoring features, to check for changes as well as errors faced by the application.

Including:
- **Logs**: View application logs in real-time through the Render dashboard.
- **Metrics**: Track resource usage, including CPU, memory, and disk utilization.
- **Alerts**: Configure alerts to notify the team if the application fails or exceeds resource limits.

---

## Project Structure

```bash
ecommerce/
├── shop/*
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── context_processors.py
│   ├── management/
│   │   ├── commands/*
├── ecommerce/
│   ├── settings.py
│   ├── urls.py
├── theme/
│   ├── apps.py
│   ├── urls.py
│   ├── static_src/
│   │   ├── src/*
│   │   │   ├── src/*
│   │   │   │   ├── package.json
│   │   │   │   ├── postcss.config.js
│   │   │   │   ├── tailwind.config.js
│   ├── templates/*
│   │   ├── base.html
├── requirements.txt
├── Dockerfile
└── README.md
```

## Future enhancements
Below are some of the pendding features to implement, as well as posible future changes to the application.
1. **Checkout Process**:  
   - Implement a fully functional checkout system, including payment gateway integration (e.g., Stripe or PayPal) to process user transactions securely.

2. **Kubernetes Support**:  
   - Add container orchestration for larger-scale deployments.

3. **Search and Filtering**:  
   - Add advanced search and filtering options to improve user experience.

## Contribution
