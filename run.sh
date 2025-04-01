#!/bin/bash

# Make this script executable
chmod +x run.sh

# Check if running in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Activating virtual environment..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "Virtual environment not found. Creating one..."
        python3 -m venv .venv
        source .venv/bin/activate
        echo "Installing dependencies..."
        pip install -r requirements.txt
    fi
fi

# Run the app with better debugging info
echo "Starting Emotional Journal App..."
python app.py