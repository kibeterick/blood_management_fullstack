#!/bin/bash
# Deployment script for blood inventory visualization on PythonAnywhere
# Run this script in the PythonAnywhere Bash console

echo "=========================================="
echo "Blood Inventory Deployment Script"
echo "=========================================="
echo ""

# Navigate to project directory
echo "1. Navigating to project directory..."
cd ~/blood_management_fullstack

# Pull latest changes from GitHub
echo "2. Pulling latest changes from GitHub..."
git pull origin main

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate

# Populate blood inventory database