#!/usr/bin/env python3
"""
Side Hustle Suggestion Viewer

This script creates a simple HTML-based viewer for side hustle suggestions.
It scans the suggestions directory, extracts metadata from markdown files,
and generates an index.html file with a clean interface for browsing suggestions.
"""

import os
import re
import datetime
import json
import webbrowser
from pathlib import Path
import markdown
import argparse

# Constants
SUGGESTIONS_DIR = "example-suggestions"
INDEX_FILE = os.path.join(SUGGESTIONS_DIR, "index.html")
ASSETS_DIR = os.path.join(SUGGESTIONS_DIR, "assets")

def extract_metadata(file_path):
    """Extract metadata from a suggestion markdown file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract the suggestion title (Side Hustle Name)
        title_match = re.search(r'##\s+([^\n]+)', content)
        title = title_match.group(1).strip() if title_match else "Untitled Suggestion"
        
        # Extract the summary section if it exists
        summary_match = re.search(r'##\s+Summary\s*\n+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else "No summary available."
        
        # Extract the rating if it exists
        rating_match = re.search(r'##\s+Side-Hustle-Ometer\s*\n+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        rating_text = rating_match.group(1).strip() if rating_match else ""
        rating = None
        if rating_text:
            rating_number_match = re.search(r'(\d+(?:\.\d+)?)\s*\/\s*10', rating_text)
            if rating_number_match:
                try:
                    rating = float(rating_number_match.group(1))
                except ValueError:
                    pass
        
        # Get file creation date
        file_stats = os.stat(file_path)
        creation_date = datetime.datetime.fromtimestamp(file_stats.st_ctime)
        
        # Extract file number prefix (if any)
        file_name = os.path.basename(file_path)
        number_match = re.match(r'(\d+)-', file_name)
        number = int(number_match.group(1)) if number_match else 0
        
        return {
            "title": title,
            "summary": summary,
            "rating": rating,
            "creation_date": creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": os.path.relpath(file_path, SUGGESTIONS_DIR),
            "number": number
        }
    except Exception as e:
        print(f"Error extracting metadata from {file_path}: {e}")
        return {
            "title": os.path.basename(file_path),
            "summary": "Error reading this suggestion.",
            "rating": None,
            "creation_date": "Unknown",
            "file_path": os.path.relpath(file_path, SUGGESTIONS_DIR),
            "number": 0
        }

def create_suggestion_html(suggestion_path):
    """Convert a markdown suggestion to HTML."""
    try:
        with open(suggestion_path, 'r') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content)
        
        # Add some basic styling
        styled_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Side Hustle Suggestion</title>
            <link rel="stylesheet" href="assets/styles.css">
        </head>
        <body>
            <div class="container suggestion-detail">
                <a href="index.html" class="back-link">← Back to all suggestions</a>
                <div class="suggestion-content">
                    {html_content}
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save the HTML file
        html_path = os.path.splitext(suggestion_path)[0] + ".html"
        with open(html_path, 'w') as f:
            f.write(styled_html)
        
        return os.path.relpath(html_path, SUGGESTIONS_DIR)
    except Exception as e:
        print(f"Error creating HTML for {suggestion_path}: {e}")
        return None

def create_assets():
    """Create CSS and other assets for the viewer."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # Create CSS file
    css_content = """
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #f8f9fa;
        padding: 20px;
    }
    
    .container {
        max-width: 1000px;
        margin: 0 auto;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        padding: 30px;
    }
    
    h1 {
        margin-bottom: 20px;
        color: #2c3e50;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
    }
    
    .filters {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .search-box {
        padding: 8px 15px;
        border: 1px solid #ddd;
        border-radius: 4px;
        width: 250px;
        font-size: 14px;
    }
    
    .sort-options {
        display: flex;
        gap: 10px;
    }
    
    .sort-btn {
        background-color: #f0f0f0;
        border: none;
        padding: 8px 15px;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .sort-btn:hover, .sort-btn.active {
        background-color: #e0e0e0;
    }
    
    .suggestion-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .suggestion-card {
        border: 1px solid #eee;
        border-radius: 6px;
        padding: 20px;
        transition: transform 0.2s, box-shadow 0.2s;
        background-color: white;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .suggestion-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .suggestion-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .suggestion-meta {
        color: #7f8c8d;
        font-size: 14px;
        margin-bottom: 10px;
    }
    
    .suggestion-rating {
        display: inline-block;
        padding: 3px 8px;
        background-color: #f39c12;
        color: white;
        border-radius: 4px;
        font-weight: bold;
        margin-right: 10px;
    }
    
    .suggestion-summary {
        flex-grow: 1;
        margin-bottom: 15px;
        font-size: 14px;
        color: #555;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
    }
    
    .suggestion-link {
        display: inline-block;
        padding: 8px 15px;
        background-color: #3498db;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        text-align: center;
        transition: background-color 0.2s;
    }
    
    .suggestion-link:hover {
        background-color: #2980b9;
    }
    
    .back-link {
        display: inline-block;
        margin-bottom: 20px;
        color: #3498db;
        text-decoration: none;
    }
    
    .back-link:hover {
        text-decoration: underline;
    }
    
    .suggestion-detail h1 {
        margin-top: 20px;
    }
    
    .suggestion-detail h2 {
        margin-top: 25px;
        margin-bottom: 15px;
        color: #2c3e50;
    }
    
    .suggestion-detail p {
        margin-bottom: 15px;
    }
    
    .no-suggestions {
        text-align: center;
        padding: 40px;
        color: #7f8c8d;
    }
    
    @media (max-width: 768px) {
        .filters {
            flex-direction: column;
            gap: 10px;
        }
        
        .search-box {
            width: 100%;
        }
        
        .suggestion-list {
            grid-template-columns: 1fr;
        }
    }
    """
    
    with open(os.path.join(ASSETS_DIR, "styles.css"), 'w') as f:
        f.write(css_content)
    
    # Create JavaScript file
    js_content = """
    document.addEventListener('DOMContentLoaded', function() {
        const searchBox = document.getElementById('search-box');
        const suggestionCards = document.querySelectorAll('.suggestion-card');
        const sortDateBtn = document.getElementById('sort-date');
        const sortRatingBtn = document.getElementById('sort-rating');
        const sortNumberBtn = document.getElementById('sort-number');
        const suggestionList = document.querySelector('.suggestion-list');
        
        // Search functionality
        searchBox.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            suggestionCards.forEach(card => {
                const title = card.querySelector('.suggestion-title').textContent.toLowerCase();
                const summary = card.querySelector('.suggestion-summary').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || summary.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
        
        // Sorting functionality
        function sortCards(sortBy) {
            const cardsArray = Array.from(suggestionCards);
            
            if (sortBy === 'date') {
                cardsArray.sort((a, b) => {
                    const dateA = new Date(a.dataset.date);
                    const dateB = new Date(b.dataset.date);
                    return dateB - dateA; // Newest first
                });
                
                sortDateBtn.classList.add('active');
                sortRatingBtn.classList.remove('active');
                sortNumberBtn.classList.remove('active');
            } 
            else if (sortBy === 'rating') {
                cardsArray.sort((a, b) => {
                    const ratingA = parseFloat(a.dataset.rating || 0);
                    const ratingB = parseFloat(b.dataset.rating || 0);
                    return ratingB - ratingA; // Highest first
                });
                
                sortDateBtn.classList.remove('active');
                sortRatingBtn.classList.add('active');
                sortNumberBtn.classList.remove('active');
            }
            else if (sortBy === 'number') {
                cardsArray.sort((a, b) => {
                    const numA = parseInt(a.dataset.number || 0);
                    const numB = parseInt(b.dataset.number || 0);
                    return numB - numA; // Highest first
                });
                
                sortDateBtn.classList.remove('active');
                sortRatingBtn.classList.remove('active');
                sortNumberBtn.classList.add('active');
            }
            
            // Reappend in new order
            cardsArray.forEach(card => {
                suggestionList.appendChild(card);
            });
        }
        
        // Add event listeners for sorting
        if (sortDateBtn) sortDateBtn.addEventListener('click', () => sortCards('date'));
        if (sortRatingBtn) sortRatingBtn.addEventListener('click', () => sortCards('rating'));
        if (sortNumberBtn) sortNumberBtn.addEventListener('click', () => sortCards('number'));
        
        // Initialize with date sort
        if (sortDateBtn) sortDateBtn.click();
    });
    """
    
    with open(os.path.join(ASSETS_DIR, "script.js"), 'w') as f:
        f.write(js_content)

def generate_index_html(suggestions):
    """Generate the index.html file with all suggestions."""
    # Create the suggestions directory if it doesn't exist
    os.makedirs(SUGGESTIONS_DIR, exist_ok=True)
    
    # Create assets (CSS, JS)
    create_assets()
    
    # Sort suggestions by creation date (newest first)
    sorted_suggestions = sorted(
        suggestions, 
        key=lambda x: datetime.datetime.strptime(x["creation_date"], "%Y-%m-%d %H:%M:%S"), 
        reverse=True
    )
    
    # Generate HTML for each suggestion card
    suggestion_cards = ""
    for suggestion in sorted_suggestions:
        rating_html = ""
        if suggestion["rating"]:
            rating_html = f'<span class="suggestion-rating">{suggestion["rating"]}/10</span>'
        
        # Get HTML path
        html_path = os.path.splitext(suggestion["file_path"])[0] + ".html"
        
        suggestion_cards += f"""
        <div class="suggestion-card" data-date="{suggestion['creation_date']}" data-rating="{suggestion['rating'] or 0}" data-number="{suggestion['number']}">
            <div class="suggestion-title">{suggestion['title']}</div>
            <div class="suggestion-meta">
                {rating_html}
                <span>{suggestion['creation_date']}</span>
            </div>
            <div class="suggestion-summary">{suggestion['summary']}</div>
            <a href="{html_path}" class="suggestion-link">View Suggestion</a>
        </div>
        """
    
    # If no suggestions, show a message
    if not suggestion_cards:
        suggestion_cards = '<div class="no-suggestions">No suggestions found. Generate some using the Side Hustle Ideation Agent!</div>'
    
    # Create the HTML file
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Side Hustle Suggestions</title>
        <link rel="stylesheet" href="assets/styles.css">
    </head>
    <body>
        <div class="container">
            <h1>Side Hustle Suggestions</h1>
            
            <div class="filters">
                <input type="text" id="search-box" class="search-box" placeholder="Search suggestions...">
                <div class="sort-options">
                    <button id="sort-number" class="sort-btn">Sort by Number</button>
                    <button id="sort-date" class="sort-btn active">Sort by Date</button>
                    <button id="sort-rating" class="sort-btn">Sort by Rating</button>
                </div>
            </div>
            
            <div class="suggestion-list">
                {suggestion_cards}
            </div>
        </div>
        
        <script src="assets/script.js"></script>
    </body>
    </html>
    """
    
    # Write the HTML file
    with open(INDEX_FILE, 'w') as f:
        f.write(html_content)
    
    return INDEX_FILE

def process_suggestions():
    """Process all suggestion files and generate HTML files."""
    if not os.path.exists(SUGGESTIONS_DIR):
        os.makedirs(SUGGESTIONS_DIR, exist_ok=True)
        return []
    
    suggestions = []
    md_files = [f for f in os.listdir(SUGGESTIONS_DIR) if f.endswith('.md')]
    
    for md_file in md_files:
        file_path = os.path.join(SUGGESTIONS_DIR, md_file)
        
        # Extract metadata
        metadata = extract_metadata(file_path)
        suggestions.append(metadata)
        
        # Create HTML version
        create_suggestion_html(file_path)
    
    return suggestions

def main():
    """Main function to run the suggestion viewer."""
    parser = argparse.ArgumentParser(description="Side Hustle Suggestion Viewer")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()
    
    print("\n📊 Side Hustle Suggestion Viewer 📊\n")
    
    # Process suggestion files
    suggestions = process_suggestions()
    
    if not suggestions:
        print("No suggestion files found in the 'suggestions' directory.")
        print("Generate some suggestions first using the Side Hustle Ideation Agent.")
        return
    
    # Generate the index HTML
    index_file = generate_index_html(suggestions)
    
    print(f"✅ Generated suggestion viewer at {index_file}")
    print(f"Found {len(suggestions)} suggestion(s)")
    
    # Open in browser if requested
    if not args.no_browser:
        index_url = f"file://{os.path.abspath(index_file)}"
        print(f"Opening {index_url} in your browser...")
        webbrowser.open(index_url)
    
    print("\nYou can view your suggestions anytime by running this script again.")

if __name__ == "__main__":
    main()
