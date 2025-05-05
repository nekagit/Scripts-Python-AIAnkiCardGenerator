# Anki Card Generator

A Python application for generating and managing Anki flashcards with Google's Gemini AI integration.

## Features

- Create Anki cards from text files
- Create Anki cards from CSV files
- Create and manage folders for organizing cards
- Generate flashcards automatically using Google's Gemini AI
- Visual folder selection using Tkinter dialogs
- Batch create folders and cards

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/anki-card-generator.git
   cd anki-card-generator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

### Menu Options

1. **Create Anki cards from text file** - Import cards from tab-separated text files
2. **Create Anki cards from CSV file** - Import cards from CSV files with custom delimiters
3. **Create folder for Anki cards** - Create a new folder for organizing cards
4. **Generate Anki cards with Gemini AI** - Use Google's Gemini AI to generate cards on any topic
5. **Batch create folders and cards** - Create multiple folders and card sets at once
6. **Open folder and create cards by topic** - Select a folder and create cards for a specific topic
7. **Exit** - Exit the application

## Gemini AI Integration

To use the Gemini AI features, you'll need a Google API key with access to the Gemini API. 
Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Project Structure

- `main.py` - Main application and UI logic
- `anki_utils.py` - Utility functions for file operations
- `gemini_generator.py` - Integration with Google's Gemini AI

## Requirements

- Python 3.7+
- `google-generativeai` package
- Tkinter (usually comes with Python)

## License

MIT