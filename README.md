# Side Hustle Ideation Agent

An AI-powered tool that generates personalized side hustle suggestions based on your professional profile.

## Overview

The Side Hustle Ideation Agent uses Ollama with Llama models to analyze your professional background and generate creative, tailored side hustle ideas. Each suggestion is saved as a detailed markdown file in the `example-suggestions` folder.

## Features

- Uses local LLM models via Ollama (preferably LLAMA 3.2)
- Customizable creativity level (1-5 scale)
- Generates detailed side hustle suggestions with:
  - Rationale based on your background
  - Market opportunity analysis
  - Target market identification
  - Collaboration suggestions
  - Networking strategies
  - Remote-friendliness assessment
  - Strengths and weaknesses analysis
  - Side-Hustle-Ometer rating (1-10)

## Prerequisites

- Python 3.6+
- [Ollama](https://ollama.ai/) installed and running
- LLAMA model pulled in Ollama (preferably LLAMA 3.2)

## Quick Installation

Use the provided installation script:

```bash
chmod +x install.sh
./install.sh
```

This script will:
1. Check for Python and pip
2. Verify if Ollama is installed
3. Create a virtual environment
4. Install dependencies
5. Set up a user profile template
6. Create necessary directories
7. Make scripts executable

## Manual Installation

1. Clone this repository
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make sure Ollama is running with LLAMA models available:
   ```bash
   ollama pull llama3
   ```

## Usage

1. Update your profile in `user-data/user-profile.json` with your professional information
2. Run the agent:
   ```bash
   # If you used the install script
   ./run.sh
   
   # Or manually
   python scripts/side_hustle_ideation_agent.py
   ```
3. Follow the prompts to specify:
   - Type of suggestion (Side Hustle Ideas)
   - Number of suggestions to generate
   - Creativity level (1-5)
4. Check the `example-suggestions` folder for your generated side hustle ideas

## Viewing Suggestions

You can view your generated suggestions using the suggestion viewer:

```bash
# If you used the install script
./view.sh

# Or manually
python scripts/suggestion_viewer.py
```

## Creativity Levels

- **Level 1**: Conservative ideas based directly on your experience
- **Level 2**: Moderate creativity with familiar concepts
- **Level 3**: Balanced creativity with some novel ideas
- **Level 4**: High creativity with innovative concepts
- **Level 5**: Maximum creativity with unconventional, potentially disruptive ideas

## Repository Structure

```
Side-Hustle-Ideation-Agent/
├── agent-configuration/         # Agent configuration files
│   └── side-hustles/            # Side hustle specific configuration
│       ├── ai-personality.md    # Agent personality definition
│       ├── context.md           # Context processing guidelines
│       ├── guardrails.md        # Ethical guardrails
│       ├── parameters.md        # Parameter settings
│       ├── response-template.md # Template for suggestions
│       └── system-prompt.md     # Main system prompt
├── example-suggestions/         # Generated suggestions are stored here
├── scripts/                     # Python scripts
│   ├── side_hustle_ideation_agent.py  # Main agent script
│   └── suggestion_viewer.py     # Tool to view suggestions
├── user-data/                   # User profile data
│   └── user-profile.json        # Your professional profile
├── install.sh                   # Installation script
├── run.sh                       # Script to run the agent
├── view.sh                      # Script to view suggestions
└── requirements.txt             # Python dependencies
```

## License

[MIT License](LICENSE)
