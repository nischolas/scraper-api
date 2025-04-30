#!/bin/bash

set -e

echo "Starting setup process..."

if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it first."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found!"
    exit 1
fi

if [ -z "$(pip freeze)" ]; then
    echo "No packages found. Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "Packages already installed"
fi

if [ ! -f "main.py" ]; then
    echo "main.py not found!"
    exit 1
fi

echo "Starting Flask server..."
python3 main.py