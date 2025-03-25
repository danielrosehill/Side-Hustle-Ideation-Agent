# Side Hustle Ideation Agent

An AI-powered tool that generates personalized side hustle suggestions based on your professional profile.

## Overview

The Side Hustle Ideation Agent uses Ollama with LLAMA models to analyze your professional background and generate creative, tailored side hustle ideas. Each suggestion is saved as a detailed markdown file in the `suggestions` folder.

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

## Prerequisites

- Python 3.6+
- [Ollama](https://ollama.ai/) installed and running
- LLAMA model pulled in Ollama (preferably LLAMA 3.2)

## Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install requests
   ```
3. Make sure Ollama is running with LLAMA models available

## Usage

1. Update your profile in `model/user-profile.json` with your professional information
2. Run the script:
   ```
   python side_hustle_ideation_agent.py
   ```
3. Follow the prompts to specify:
   - Number of suggestions to generate
   - Creativity level (1-5)
4. Check the `suggestions` folder for your generated side hustle ideas

## Creativity Levels

- **Level 1**: Conservative ideas based directly on your experience
- **Level 2**: Moderate creativity with familiar concepts
- **Level 3**: Balanced creativity with some novel ideas
- **Level 4**: High creativity with innovative concepts
- **Level 5**: Maximum creativity with unconventional, potentially disruptive ideas

## License

[MIT License](LICENSE)
