#!/bin/bash

# Side Hustle Ideation Agent - Suggestion Viewer Script
# This script runs the suggestion viewer for the Side Hustle Ideation Agent

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo "Virtual environment activated"
fi

# Check if there are any suggestions to view
if [ ! -d "example-suggestions" ] || [ -z "$(ls -A example-suggestions 2>/dev/null)" ]; then
    echo "⚠️ No suggestions found in the example-suggestions directory."
    echo "Please run the Side Hustle Ideation Agent first to generate suggestions."
    echo "You can do this by executing: ./run.sh"
    exit 1
fi

# Run the suggestion viewer
echo "Starting Side Hustle Suggestion Viewer..."
python scripts/suggestion_viewer.py
