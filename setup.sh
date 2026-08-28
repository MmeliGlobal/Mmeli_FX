#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y build-essential python3-dev

# Create virtual environment with Python 3.11
python3.11 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete!"