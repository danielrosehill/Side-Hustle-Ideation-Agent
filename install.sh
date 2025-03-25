#!/bin/bash

# Side Hustle Ideation Agent - Installation Script
# This script sets up the necessary environment for running the Side Hustle Ideation Agent

set -e  # Exit on error

# Print colored text
print_color() {
    COLOR=$1
    TEXT=$2
    case $COLOR in
        "red") printf "\033[0;31m%s\033[0m\n" "$TEXT" ;;
        "green") printf "\033[0;32m%s\033[0m\n" "$TEXT" ;;
        "yellow") printf "\033[0;33m%s\033[0m\n" "$TEXT" ;;
        "blue") printf "\033[0;34m%s\033[0m\n" "$TEXT" ;;
        *) printf "%s\n" "$TEXT" ;;
    esac
}

# Check if Python 3 is installed
check_python() {
    print_color "blue" "Checking for Python 3..."
    if command -v python3 &>/dev/null; then
        print_color "green" "✓ Python 3 is installed"
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null && [[ $(python --version 2>&1) == *"Python 3"* ]]; then
        print_color "green" "✓ Python 3 is installed as 'python'"
        PYTHON_CMD="python"
    else
        print_color "red" "✗ Python 3 is not installed. Please install Python 3.6 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d " " -f 2)
    print_color "blue" "Python version: $PYTHON_VERSION"
    
    # Extract major and minor version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
        print_color "red" "✗ Python 3.6 or higher is required. You have $PYTHON_VERSION."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_color "blue" "Checking for pip..."
    if command -v pip3 &>/dev/null; then
        print_color "green" "✓ pip3 is installed"
        PIP_CMD="pip3"
    elif command -v pip &>/dev/null; then
        print_color "green" "✓ pip is installed"
        PIP_CMD="pip"
    else
        print_color "red" "✗ pip is not installed. Installing pip..."
        $PYTHON_CMD -m ensurepip --upgrade || {
            print_color "red" "Failed to install pip. Please install pip manually."
            exit 1
        }
        PIP_CMD="pip3"
    fi
}

# Check for Ollama
check_ollama() {
    print_color "blue" "Checking for Ollama..."
    if command -v ollama &>/dev/null; then
        print_color "green" "✓ Ollama is installed"
    else
        print_color "yellow" "⚠ Ollama is not installed."
        print_color "yellow" "The Side Hustle Ideation Agent requires Ollama to run locally."
        print_color "yellow" "Please install Ollama from https://ollama.com/"
        print_color "yellow" "After installing Ollama, run 'ollama pull llama3' to download the required model."
    fi
}

# Create virtual environment
create_venv() {
    print_color "blue" "Setting up virtual environment..."
    
    # Check if venv directory exists
    if [ -d "venv" ]; then
        print_color "yellow" "Virtual environment already exists. Skipping creation."
    else
        $PYTHON_CMD -m venv venv || {
            print_color "red" "Failed to create virtual environment."
            print_color "yellow" "Trying to install venv module..."
            $PIP_CMD install virtualenv
            $PYTHON_CMD -m virtualenv venv || {
                print_color "red" "Failed to create virtual environment with virtualenv."
                exit 1
            }
        }
        print_color "green" "✓ Virtual environment created"
    fi
    
    # Activate virtual environment
    print_color "blue" "Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate || {
            print_color "red" "Failed to activate virtual environment."
            exit 1
        }
    else
        source venv/bin/activate || {
            print_color "red" "Failed to activate virtual environment."
            exit 1
        }
    fi
    print_color "green" "✓ Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_color "blue" "Installing dependencies..."
    pip install -r requirements.txt || {
        print_color "red" "Failed to install dependencies."
        exit 1
    }
    print_color "green" "✓ Dependencies installed"
}

# Create user profile template if it doesn't exist
create_user_profile() {
    print_color "blue" "Checking for user profile..."
    
    if [ ! -d "user-data" ]; then
        mkdir -p user-data
    fi
    
    if [ ! -f "user-data/user-profile.json" ]; then
        print_color "yellow" "User profile not found. Creating template..."
        cat > user-data/user-profile.json << 'EOL'
{
  "user": {
    "name": "Your Name",
    "location": "Your City, Country",
    "age": 30,
    "occupation": "Your Current Job",
    "professional_experience": [
      {
        "title": "Job Title",
        "organization": "Company Name",
        "dates": "YYYY-Present",
        "description": [
          "Key responsibility or achievement",
          "Another responsibility or achievement"
        ]
      }
    ],
    "key_skills": [
      "Skill 1: Description of your proficiency",
      "Skill 2: Description of your proficiency"
    ],
    "projects": [
      {
        "name": "Project Name",
        "dates": "YYYY-Present",
        "description": "Brief description of the project"
      }
    ],
    "education": [
      {
        "degree": "Your Degree",
        "institution": "University Name"
      }
    ],
    "publications": [
      "Publication 1",
      "Publication 2"
    ],
    "awards": [
      "Award 1",
      "Award 2"
    ],
    "contact_and_online_presence": {
      "website": "https://yourwebsite.com",
      "linkedin": "https://www.linkedin.com/in/yourprofile/",
      "github": "https://github.com/yourusername",
      "citizenships": [
        "Country 1",
        "Country 2"
      ]
    },
    "ai_interests_and_preferences": {
      "preferred_work_environment": {
        "location": "Remote/Hybrid/In-office preferences",
        "engagement": "Full-time/Contract/Freelance preferences"
      },
      "strengths": [
        "Personal strength 1",
        "Personal strength 2"
      ]
    }
  }
}
EOL
        print_color "green" "✓ User profile template created at user-data/user-profile.json"
        print_color "yellow" "⚠ Please edit the user profile with your information before running the agent"
    else
        print_color "green" "✓ User profile found"
    fi
}

# Create directories for suggestions if they don't exist
create_directories() {
    print_color "blue" "Setting up directories..."
    
    if [ ! -d "example-suggestions" ]; then
        mkdir -p example-suggestions
    fi
    
    print_color "green" "✓ Directories created"
}

# Make scripts executable
make_scripts_executable() {
    print_color "blue" "Making scripts executable..."
    
    chmod +x scripts/side_hustle_ideation_agent.py
    chmod +x scripts/suggestion_viewer.py
    chmod +x run.sh
    
    print_color "green" "✓ Scripts are now executable"
}

# Main installation process
main() {
    print_color "blue" "=== Side Hustle Ideation Agent Installation ==="
    
    check_python
    check_pip
    check_ollama
    create_venv
    install_dependencies
    create_user_profile
    create_directories
    
    # Create run script
    cat > run.sh << 'EOL'
#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Run the agent
python scripts/side_hustle_ideation_agent.py "$@"
EOL
    
    # Create viewer script
    cat > view.sh << 'EOL'
#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Run the suggestion viewer
python scripts/suggestion_viewer.py
EOL
    
    chmod +x run.sh
    chmod +x view.sh
    
    print_color "green" "=== Installation Complete ==="
    print_color "yellow" "To run the Side Hustle Ideation Agent:"
    print_color "blue" "1. Make sure Ollama is running"
    print_color "blue" "2. Edit your user profile in user-data/user-profile.json"
    print_color "blue" "3. Run the agent with: ./run.sh"
    print_color "blue" "4. View suggestions with: ./view.sh"
}

# Run the installation
main
