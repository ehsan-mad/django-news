#!/usr/bin/env bash
# Build script for Render

set -o errexit  # exit on error

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check database connection
echo "Testing database connection..."
python manage.py check --database default

# Show migration status
echo "Checking migration status..."
python manage.py showmigrations

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --verbosity=2

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build completed successfully!"
