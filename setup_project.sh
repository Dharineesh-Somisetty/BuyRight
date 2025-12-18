#!/bin/bash

# Exit on error
set -e

echo "Starting project setup..."

# Create directories
mkdir -p backend
mkdir -p mobile_app
mkdir -p data_pipeline

# Backend setup
echo "Setting up backend..."
touch backend/requirements.txt
mkdir -p backend/venv # venv placeholder directory

# README
echo "Initializing README..."
echo "# Apex Scanner" > README.md

# .gitignore
echo "Creating .gitignore..."
cat <<EOL > .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.venv/
*.env

# Flutter/Dart
.dart_tool/
.packages
build/
ios/Flutter/App.framework
ios/Flutter/Flutter.framework
android/**/gradle-wrapper.jar
pubspec.lock

# Mac/Windows
.DS_Store
Thumbs.db
EOL

echo "Project setup complete!"
echo "Structure created:"
ls -F
echo "Backend content:"
ls -F backend/
