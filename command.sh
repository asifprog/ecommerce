#!/bin/env bash

# Create a virtual environment if it doesn't already exist
if [ ! -d ".envs" ]; then
    echo "Creating virtual environment..."
    python -m virtualenv .envs
fi

if source .envs/bin/activate; then
    echo "Virtual environment activated."
else
    echo "Failed to activate virtual environment. Exiting..."
    exit 1
fi

if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Exiting..."
    exit 1
fi

echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Generating products..."
python manage.py generate_products

echo "Seeding products..."
python manage.py seed_products

echo "Script completed successfully."
exit 0
