#!/usr/bin/env python3
"""
Career Exploration Ideation Agent

This script generates career exploration suggestions using Ollama with LLAMA models.
It reads user profile data, prompts the user for parameters, and generates
creative suggestions saved as markdown files in category-specific folders.

Categories include:
- Side Hustle Ideas
- Career Pivot Suggestions
- Potential Employers
- Job Title Suggestions
"""

import os
import json
import time
import requests
import datetime
import sys
import re
import argparse
import importlib.util

# Constants
OLLAMA_API_URL = "http://localhost:11434/api"
USER_PROFILE_PATH = "user-data/user-profile.json"
SUGGESTIONS_DIR = "example-suggestions"
TEMPLATE_PATH = "agent-configuration/side-hustles/response-template.md"

# Category constants
CATEGORIES = {
    "side_hustle": {
        "name": "Side Hustle Ideas",
        "folder": "side_hustles",
        "template": "agent-configuration/side-hustles/response-template.md"
    },
    "career_pivot": {
        "name": "Career Pivot Suggestions",
        "folder": "career_pivots",
        "template": "agent-configuration/career-pivots/response-template.md"
    },
    "potential_employer": {
        "name": "Potential Employers",
        "folder": "potential_employers",
        "template": "agent-configuration/potential-employers/response-template.md"
    },
    "job_title": {
        "name": "Job Title Suggestions",
        "folder": "job_titles",
        "template": "agent-configuration/job-titles/response-template.md"
    }
}

def check_ollama_available():
    """Check if Ollama API is available."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        if response.status_code == 200:
            print("✅ Ollama API is available")
            return True
        else:
            print(f"❌ Ollama API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama API is not available: {e}")
        print("Make sure Ollama is running and accessible at http://localhost:11434")
        return False

def get_best_llama_model():
    """Get the best available LLAMA 3.2 model from Ollama."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            # Look for LLAMA 3.2 models
            llama_models = [model for model in models if "llama" in model["name"].lower() and "3" in model["name"]]
            
            # Sort by preference: exact match for llama3.2, then any llama3, then any llama
            if not llama_models:
                llama_models = [model for model in models if "llama" in model["name"].lower()]
                
            if llama_models:
                # Sort by version, preferring 3.2, then any 3.x, then others
                def model_score(model):
                    name = model["name"].lower()
                    if "llama3.2" in name or "llama-3.2" in name or "llama3:2" in name:
                        return 0
                    elif "llama3" in name or "llama-3" in name:
                        return 1
                    elif "llama2" in name or "llama-2" in name:
                        return 2
                    else:
                        return 3
                
                llama_models.sort(key=model_score)
                selected_model = llama_models[0]["name"]
                print(f"✅ Selected model: {selected_model}")
                return selected_model
            else:
                print("❌ No LLAMA models found. Using default 'llama3'")
                return "llama3"
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        print("Using default 'llama3' model")
        return "llama3"

def load_user_profile():
    """Load the user profile from JSON file."""
    try:
        with open(USER_PROFILE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading user profile: {e}")
        sys.exit(1)

def load_template(category_key="side_hustle"):
    """Load the suggestion template for the specified category."""
    template_path = CATEGORIES[category_key]["template"]
    try:
        with open(template_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error loading template for {CATEGORIES[category_key]['name']}: {e}")
        sys.exit(1)

def get_user_parameters():
    """Get parameters from user: category, number of suggestions and creativity level."""
    # First, let the user select a category or balanced mode
    print("\nWhat type of career exploration suggestions would you like to generate?")
    for i, (key, category) in enumerate(CATEGORIES.items(), 1):
        print(f"{i}: {category['name']}")
    print(f"{len(CATEGORIES) + 1}: Balanced Mix (equal distribution of all types)")
    
    while True:
        try:
            category_choice = int(input("\nEnter your choice (1-5): "))
            if 1 <= category_choice <= len(CATEGORIES):
                category_key = list(CATEGORIES.keys())[category_choice - 1]
                balanced_mode = False
                break
            elif category_choice == len(CATEGORIES) + 1:
                category_key = None  # Will be determined during generation
                balanced_mode = True
                break
            print(f"Please enter a number between 1 and {len(CATEGORIES) + 1}.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Predefined suggestion count options
    suggestion_options = [50, 100, 200, 500]
    print("\nHow many suggestions would you like to generate?")
    for i, count in enumerate(suggestion_options, 1):
        print(f"{i}: {count} suggestions")
    print(f"{len(suggestion_options) + 1}: Custom number")
    
    while True:
        try:
            count_choice = int(input("\nEnter your choice: "))
            if 1 <= count_choice <= len(suggestion_options):
                num_suggestions = suggestion_options[count_choice - 1]
                break
            elif count_choice == len(suggestion_options) + 1:
                num_suggestions = int(input("Enter custom number of suggestions: "))
                if num_suggestions <= 0:
                    print("Please enter a positive number.")
                    continue
                break
            print(f"Please enter a number between 1 and {len(suggestion_options) + 1}.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            creativity = int(input("\nOn a scale of 1-5, how creative should the suggestions be?\n"
                                  "1: Conservative, based on your experience\n"
                                  "5: Highly creative, unconventional ideas\n"
                                  "Your choice: "))
            if 1 <= creativity <= 5:
                break
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Map creativity level to temperature
    temperature_map = {
        1: 0.3,
        2: 0.5,
        3: 0.7,
        4: 0.9,
        5: 1.1
    }
    
    return category_key, num_suggestions, creativity, temperature_map[creativity], balanced_mode

def generate_suggestion(model, user_profile, temperature, template, category_key):
    """Generate a suggestion using the Ollama API based on the selected category."""
    # Prepare the system prompt based on category
    system_prompts = {
        "side_hustle": """You are Side Hustle Maverick, an AI assistant specialized in generating creative and personalized side hustle ideas.
Your objective is to help users build viable income streams to supplement their income and encourage them to think broadly about their career positioning.

IMPORTANT GUIDELINES:
1. Focus on DIVERSITY and ORIGINALITY in your suggestions - avoid common, overused ideas.
2. Do not overemphasize any single aspect of the user's profile - consider their full range of skills, interests, and experiences.
3. Provide detailed reasoning that connects the suggestion to multiple aspects of the user's background.
4. Consider market dynamics, trends, and realistic income potential in the user's geographic location.
5. Generate a descriptive, concise name (max 3 words) that clearly summarizes the core idea.
6. Follow the template structure exactly, filling in all sections with thoughtful content.
7. Each suggestion must be COMPLETELY DIFFERENT from any previous suggestions.

Remember that these suggestions may be used for automated processing, so consistency in format is essential.
""",
        "career_pivot": """You are Career Pivot Strategist, an AI assistant specialized in generating thoughtful and personalized career pivot suggestions.
Your objective is to help users identify new career directions that leverage their existing skills while exploring new opportunities.

IMPORTANT GUIDELINES:
1. Focus on DIVERSITY and ORIGINALITY in your suggestions - avoid common, overused career paths.
2. Do not overemphasize any single aspect of the user's profile - consider their full range of skills, interests, and experiences.
3. Provide detailed reasoning that connects the pivot to multiple aspects of the user's background.
4. Consider market dynamics, trends, and realistic career potential in the user's geographic location.
5. Generate a descriptive, concise name (max 3 words) that clearly summarizes the core direction.
6. Follow the template structure exactly, filling in all sections with thoughtful content.
7. Each suggestion must be COMPLETELY DIFFERENT from any previous suggestions.

Remember that these suggestions may be used for automated processing, so consistency in format is essential.
""",
        "potential_employer": """You are Employer Match Specialist, an AI assistant specialized in identifying potential employers that would be a good fit for the user.
Your objective is to help users discover organizations where they could thrive based on their skills, experience, and preferences.

IMPORTANT GUIDELINES:
1. Focus on DIVERSITY and ORIGINALITY in your suggestions - include a mix of established companies, startups, non-profits, and other organization types.
2. Do not overemphasize any single aspect of the user's profile - consider their full range of skills, interests, and experiences.
3. Provide detailed reasoning that connects the employer to multiple aspects of the user's background.
4. Consider company culture, growth potential, and alignment with the user's values and location preferences.
5. Generate a descriptive, concise name (max 3 words) that clearly summarizes the type of organization.
6. Follow the template structure exactly, filling in all sections with thoughtful content.
7. Each suggestion must be COMPLETELY DIFFERENT from any previous suggestions.

Remember that these suggestions may be used for automated processing, so consistency in format is essential.
""",
        "job_title": """You are Job Title Explorer, an AI assistant specialized in identifying potential job titles and roles that would be a good fit for the user.
Your objective is to help users discover positions where they could thrive based on their skills, experience, and preferences.

IMPORTANT GUIDELINES:
1. Focus on DIVERSITY and ORIGINALITY in your suggestions - include a mix of traditional, emerging, and niche job titles.
2. Do not overemphasize any single aspect of the user's profile - consider their full range of skills, interests, and experiences.
3. Provide detailed reasoning that connects the job title to multiple aspects of the user's background.
4. Consider role responsibilities, growth potential, and alignment with the user's skills and interests.
5. Generate a descriptive, concise job title (max 3 words) that clearly summarizes the role.
6. Follow the template structure exactly, filling in all sections with thoughtful content.
7. Each suggestion must be COMPLETELY DIFFERENT from any previous suggestions.

Remember that these suggestions may be used for automated processing, so consistency in format is essential.
"""
    }
    
    # Prepare the user prompt based on category
    user_prompts = {
        "side_hustle": f"""Based on the following user profile, generate ONE creative side hustle idea.
The idea should be tailored to the user's skills, experience, and interests.
Follow the template structure exactly, filling in all sections with thoughtful content.
Make sure this suggestion is COMPLETELY DIFFERENT from any previous suggestions.

USER PROFILE:
{json.dumps(user_profile, indent=2)}

TEMPLATE TO FOLLOW:
{template}

Generate a complete side hustle suggestion following the template structure above.
Ensure the side hustle name is descriptive and concise (maximum 3 words).
""",
        "career_pivot": f"""Based on the following user profile, generate ONE creative career pivot suggestion.
The suggestion should be tailored to the user's skills, experience, and interests.
Follow the template structure exactly, filling in all sections with thoughtful content.
Make sure this suggestion is COMPLETELY DIFFERENT from any previous suggestions.

USER PROFILE:
{json.dumps(user_profile, indent=2)}

TEMPLATE TO FOLLOW:
{template}

Generate a complete career pivot suggestion following the template structure above.
Ensure the career pivot name is descriptive and concise (maximum 3 words).
""",
        "potential_employer": f"""Based on the following user profile, identify ONE potential employer that would be a good fit.
The suggestion should be tailored to the user's skills, experience, and interests.
Follow the template structure exactly, filling in all sections with thoughtful content.
Make sure this suggestion is COMPLETELY DIFFERENT from any previous suggestions.

USER PROFILE:
{json.dumps(user_profile, indent=2)}

TEMPLATE TO FOLLOW:
{template}

Generate a complete potential employer suggestion following the template structure above.
Ensure the employer name is descriptive and concise (maximum 3 words).
""",
        "job_title": f"""Based on the following user profile, suggest ONE potential job title that would be a good fit.
The suggestion should be tailored to the user's skills, experience, and interests.
Follow the template structure exactly, filling in all sections with thoughtful content.
Make sure this suggestion is COMPLETELY DIFFERENT from any previous suggestions.

USER PROFILE:
{json.dumps(user_profile, indent=2)}

TEMPLATE TO FOLLOW:
{template}

Generate a complete job title suggestion following the template structure above.
Ensure the job title is descriptive and concise (maximum 3 words).
"""
    }

    system_prompt = system_prompts[category_key]
    user_prompt = user_prompts[category_key]

    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/generate",
            json={
                "model": model,
                "prompt": user_prompt,
                "system": system_prompt,
                "temperature": temperature,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"❌ Error generating suggestion: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error calling Ollama API: {e}")
        return None

def extract_title(suggestion_text):
    """Extract a descriptive title from the generated suggestion.
    
    Returns a kebab-case title with maximum 3 words that summarizes the idea.
    """
    # Look for the first heading after "Side Hustle Name" or similar
    match = re.search(r'##\s+([^\n]+)', suggestion_text)
    if match:
        title = match.group(1).strip()
        
        # Clean and format the title (max 3 words, kebab-case)
        words = re.sub(r'[^\w\s-]', '', title).strip().split()
        if len(words) > 3:
            words = words[:3]
        
        kebab_title = '-'.join(words).lower()
        return kebab_title
    
    # Fallback to timestamp if no title found
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"suggestion-{timestamp}"

def save_suggestion(suggestion_text, index, category_key):
    """Save the suggestion to a markdown file in the appropriate category folder."""
    # Create the main suggestions directory if it doesn't exist
    if not os.path.exists(SUGGESTIONS_DIR):
        os.makedirs(SUGGESTIONS_DIR)
    
    # Create the category-specific folder if it doesn't exist
    category_folder = os.path.join(SUGGESTIONS_DIR, CATEGORIES[category_key]["folder"])
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)
    
    # Extract a title from the suggestion
    title = extract_title(suggestion_text)
    
    # Add index to filename to avoid collisions
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"{timestamp}-{index+1:02d}-{title}.md"
    filepath = os.path.join(category_folder, filename)
    
    # Save the suggestion to a file
    try:
        with open(filepath, 'w') as f:
            f.write(suggestion_text)
        print(f"✅ Saved suggestion to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving suggestion: {e}")
        return False

def main():
    """Main function to run the ideation agent."""
    parser = argparse.ArgumentParser(description='Career Exploration Ideation Agent')
    parser.add_argument('--check-dependencies', action='store_true', 
                        help='Check if all required dependencies are installed')
    args = parser.parse_args()
    
    # Check dependencies if requested
    if args.check_dependencies:
        dependencies = ['requests']
        missing = []
        for dep in dependencies:
            if importlib.util.find_spec(dep) is None:
                missing.append(dep)
        
        if missing:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            print("Please install them using: pip install " + " ".join(missing))
            sys.exit(1)
        else:
            print("✅ All dependencies are installed")
            sys.exit(0)
    
    print("\n🔍 Career Exploration Ideation Agent 🔍\n")
    
    # Check if Ollama is available
    if not check_ollama_available():
        sys.exit(1)
    
    # Get the best available LLAMA model
    model = get_best_llama_model()
    
    # Load user profile
    user_profile = load_user_profile()
    print(f"✅ Loaded user profile for {user_profile['user']['name']}")
    
    # Get user parameters
    category_key, num_suggestions, creativity, temperature, balanced_mode = get_user_parameters()
    
    if balanced_mode:
        # Calculate how many suggestions to generate for each category
        categories_count = len(CATEGORIES)
        suggestions_per_category = num_suggestions // categories_count
        remainder = num_suggestions % categories_count
        
        # Distribute remainder evenly
        category_counts = {key: suggestions_per_category for key in CATEGORIES.keys()}
        for i, key in enumerate(CATEGORIES.keys()):
            if i < remainder:
                category_counts[key] += 1
        
        print(f"\nGenerating a balanced mix of {num_suggestions} suggestions with creativity level {creativity} (temperature: {temperature:.1f})")
        print("Distribution:")
        for key, count in category_counts.items():
            print(f"- {CATEGORIES[key]['name']}: {count} suggestions")
        
        # Generate and save suggestions for each category
        successful = 0
        for category_key, count in category_counts.items():
            print(f"\n📂 Generating {count} {CATEGORIES[category_key]['name']}...")
            
            # Load template for this category
            template = load_template(category_key)
            
            for i in range(count):
                print(f"\n🧠 Generating {CATEGORIES[category_key]['name']} suggestion {i+1}/{count}...")
                
                suggestion = generate_suggestion(model, user_profile, temperature, template, category_key)
                if suggestion:
                    if save_suggestion(suggestion, i, category_key):
                        successful += 1
                    time.sleep(1)  # Small delay between generations
        
        # Summary
        print(f"\n✅ Successfully generated {successful}/{num_suggestions} suggestions across all categories.")
        print(f"📁 Suggestions saved to {SUGGESTIONS_DIR}/ in their respective category folders")
    else:
        print(f"\nGenerating {num_suggestions} {CATEGORIES[category_key]['name']} with creativity level {creativity} (temperature: {temperature:.1f})")
        
        # Load template for the selected category
        template = load_template(category_key)
        
        # Generate and save suggestions
        successful = 0
        for i in range(num_suggestions):
            print(f"\n🧠 Generating suggestion {i+1}/{num_suggestions}...")
            
            suggestion = generate_suggestion(model, user_profile, temperature, template, category_key)
            if suggestion:
                if save_suggestion(suggestion, i, category_key):
                    successful += 1
                time.sleep(1)  # Small delay between generations
        
        # Summary
        print(f"\n✅ Successfully generated {successful}/{num_suggestions} {CATEGORIES[category_key]['name']}.")
        print(f"📁 Suggestions saved to {os.path.join(SUGGESTIONS_DIR, CATEGORIES[category_key]['folder'])}/")

if __name__ == "__main__":
    main()
