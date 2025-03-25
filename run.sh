#!/bin/bash

# Side Hustle Ideation Agent - Run Script
# This script runs the Side Hustle Ideation Agent

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo "Virtual environment activated"
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️ Warning: Ollama doesn't appear to be running."
    echo "Please start Ollama before continuing."
    echo "You can download Ollama from https://ollama.com/ if not installed."
    
    read -p "Continue anyway? (y/n): " continue_choice
    if [[ ! $continue_choice =~ ^[Yy]$ ]]; then
        echo "Exiting. Please start Ollama and try again."
        exit 1
    fi
fi

# Run the agent
echo "Starting Side Hustle Ideation Agent..."
python scripts/side_hustle_ideation_agent.py "$@"
