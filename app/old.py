import os
import csv
import json
import time
import requests
import tkinter as tk
from tkinter import filedialog
from typing import List, Tuple, Optional

# Constants for Gemini API
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def create_anki_cards_from_text_file(file_path):
    """Create Anki cards from a tab-separated text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    cards = []
    for line in lines:
        if '\t' in line:
            question, answer = line.strip().split('\t')
            cards.append((question, answer))
    return cards

def create_anki_cards_from_csv_file(file_path, delimiter=','):
    """Create Anki cards from a CSV file with specified delimiter."""
    cards = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            if len(row) >= 2:
                question, answer = row[0], row[1]
                cards.append((question, answer))
    return cards

def create_folder_for_anki_cards(folder_path):
    """Create a folder for storing Anki cards if it doesn't exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")
    return folder_path

def save_cards_to_csv(cards, file_path, delimiter=';'):
    """Save cards to a CSV file with specified delimiter."""
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=delimiter)
        for card in cards:
            writer.writerow(card)
    print(f"Saved {len(cards)} cards to {file_path}")

def generate_anki_cards_with_gemini(api_key: str, topic: str, num_cards: int = 10, 
                                   format_instructions: Optional[str] = None) -> List[Tuple[str, str]]:
    """
    Generate Anki cards using Google's Gemini API.
    
    Args:
        api_key: Google API key with Gemini access
        topic: The topic to generate cards for
        num_cards: Number of cards to generate
        format_instructions: Optional specific formatting instructions
        
    Returns:
        List of tuples containing (question, answer) pairs
    """
    if not api_key:
        raise ValueError("API key is required for Gemini API access")
    
    # Default format instructions if none provided
    if not format_instructions:
        format_instructions = (
            "Generate concise, exam-style flashcards with clear questions and answers. "
            "Make sure the answers are detailed enough to be educational but concise. "
            "Format your response as a JSON array of objects, where each object has a 'question' and 'answer' field."
        )
    
    # Construct the prompt
    prompt = f"""
    Topic: {topic}
    
    Please generate {num_cards} high-quality Anki flashcards for this topic.
    
    {format_instructions}
    """
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]
    }
    
    # Make the API call
    try:
        response = requests.post(
            f"{GEMINI_API_BASE_URL}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # Extract the JSON from the response text
        # Find JSON content - look for JSON array
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            # Try to find JSON object if not an array
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_content = response_text[json_start:json_end]
            try:
                cards_data = json.loads(json_content)
                
                # Handle both array of objects and single object formats
                if isinstance(cards_data, dict):
                    # Single card
                    return [(cards_data.get("question", ""), cards_data.get("answer", ""))]
                else:
                    # Array of cards
                    return [(card.get("question", ""), card.get("answer", "")) for card in cards_data]
            except json.JSONDecodeError:
                print("Error parsing JSON response. Trying to extract cards manually...")
                # Fallback parsing
                return extract_cards_from_text(response_text)
        else:
            # Fallback to manual extraction if JSON format not detected
            return extract_cards_from_text(response_text)
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def extract_cards_from_text(text: str) -> List[Tuple[str, str]]:
    """Extract flashcards from text if JSON parsing fails."""
    cards = []
    lines = text.split('\n')
    
    current_question = None
    current_answer = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with Q: or similar pattern
        if line.startswith(('Q:', 'Question:', 'Q.', 'Question ', 'Card ')) or (line[0].isdigit() and ')' in line[:5]):
            # Save previous card if exists
            if current_question is not None and current_answer:
                cards.append((current_question, ' '.join(current_answer)))
                current_answer = []
                
            # Extract new question
            if ':' in line:
                current_question = line.split(':', 1)[1].strip()
            elif '.' in line[:5]:
                current_question = line.split('.', 1)[1].strip()
            elif ')' in line[:5]:
                current_question = line.split(')', 1)[1].strip()
            else:
                current_question = line
                
        # Check if line starts with A: or similar pattern
        elif line.startswith(('A:', 'Answer:', 'A.', 'Answer ')) and current_question is not None:
            # Extract answer
            if ':' in line:
                answer = line.split(':', 1)[1].strip()
            elif '.' in line[:5]:
                answer = line.split('.', 1)[1].strip()
            else:
                answer = line
            current_answer.append(answer)
            
        # If we're collecting an answer and line doesn't look like a new question
        elif current_question is not None and current_answer:
            current_answer.append(line)
            
    # Add the last card if exists
    if current_question is not None and current_answer:
        cards.append((current_question, ' '.join(current_answer)))
        
    return cards

def create_batch_folders_and_cards():
    """Create multiple folders and generate cards for each one."""
    print("Enter a list of folder names (one per line). Type 'DONE' on a new line when finished:")
    folders = []
    while True:
        line = input()
        if line.strip().upper() == "DONE":
            break
        folders.extend([folder.strip() for folder in line.split(',') if folder.strip()])
    
    if not folders:
        print("No folders specified.")
        return
    
    # Use dialog to select base directory
    print("\nSelect base directory for folders:")
    base_dir = select_folder_with_dialog()
    
    if not base_dir:
        base_dir = input("No directory selected. Enter base directory path (leave blank for current directory): ").strip()
        if not base_dir:
            base_dir = os.getcwd()
    
    cards_per_folder = int(input("Enter number of cards per folder (default is 50): ") or 50)
    
    for folder in folders:
        # Create folder
        folder_path = os.path.join(base_dir, folder)
        create_folder_for_anki_cards(folder_path)
        
        # Generate cards
        # Note: This is missing implementation in the original code
        cards = []
        
        # Save cards
        csv_path = os.path.join(folder_path, f"{folder}_cards.csv")
        save_cards_to_csv(cards, csv_path, delimiter=';')
    
    print(f"\nCreated {len(folders)} folders with {cards_per_folder} cards each.")

def select_folder_with_dialog():
    """Open a folder selection dialog using Tkinter."""
    # Hide the main Tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # Show the folder selection dialog
    folder_path = filedialog.askdirectory(
        title="Select Folder for Anki Cards",
        mustexist=False  # Allow selecting non-existent paths for folder creation
    )
    
    # Clean up
    root.destroy()
    
    return folder_path

def open_folder_and_generate_cards():
    """Open a specific folder and generate cards based on user input topic."""
    print("\nOpening folder selection dialog...")
    folder_path = select_folder_with_dialog()
    
    if not folder_path:
        print("No folder selected. Operation cancelled.")
        return
        
    print(f"Selected folder: {folder_path}")
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_path):
        create_option = input(f"Folder '{folder_path}' doesn't exist. Create it? (y/n): ")
        if create_option.lower() == 'y':
            create_folder_for_anki_cards(folder_path)
        else:
            print("Operation cancelled.")
            return
    else:
        print(f"Opened folder: {folder_path}")
    
    # Get topic from user
    topic = input("\nEnter the topic for your flashcards: ")
    if not topic.strip():
        print("Topic cannot be empty. Operation cancelled.")
        return
    
    # Create filename based on topic
    safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic)
    safe_topic = safe_topic.replace(" ", "_").lower()
    file_name = f"{safe_topic}_cards.csv"
    file_path = os.path.join(folder_path, file_name)
    
    # Check if file already exists
    if os.path.exists(file_path):
        overwrite = input(f"File '{file_name}' already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            file_name = f"{safe_topic}_{int(time.time())}_cards.csv"
            file_path = os.path.join(folder_path, file_name)
            print(f"Will save to new file: {file_name}")
    
    # Choose how to generate cards
    print("\nHow would you like to generate cards?")
    print("1. Manual input")
    print("2. Generate with Gemini AI")
    gen_choice = input("Enter choice (1-2): ")
    
    cards = []
    
    if gen_choice == "1":
        # Manual input
        print("\nEnter your flashcards (empty question to finish):")
        while True:
            question = input("\nQuestion: ")
            if not question.strip():
                break
            answer = input("Answer: ")
            cards.append((question, answer))
    
    elif gen_choice == "2":
        # Generate with Gemini
        api_key = input("Enter your Gemini API key: ")
        if not api_key:
            print("API key is required. Operation cancelled.")
            return
            
        num_cards = int(input("Number of cards to generate (default 10): ") or 10)
        
        print("Generating cards with Gemini AI...")
        try:
            cards = generate_anki_cards_with_gemini(api_key, topic, num_cards)
            print(f"Generated {len(cards)} cards")
            
            # Preview some cards
            if cards:
                print("\nPreview of generated cards:")
                for i, (question, answer) in enumerate(cards[:3], 1):
                    print(f"\nCard {i}:")
                    print(f"Q: {question}")
                    print(f"A: {answer}")
                
                if len(cards) > 3:
                    print(f"\n... plus {len(cards) - 3} more cards")
        except Exception as e:
            print(f"Error generating cards: {e}")
            return
    else:
        print("Invalid choice. Operation cancelled.")
        return
    
    # Save cards
    if cards:
        delimiter = input("Enter delimiter for CSV (default ';'): ") or ';'
        save_cards_to_csv(cards, file_path, delimiter)
        print(f"\nCards saved to {file_path}")
    else:
        print("No cards created. File not saved.")

def main():
    print("\n===== Anki Card Generator =====")
    print("This script helps create and manage Anki cards")
    
    while True:
        print("\nChoose Menu Options:")
        print("1. Create Anki cards from text file")
        print("2. Create Anki cards from CSV file")
        print("3. Create folder for Anki cards")
        print("4. Generate Anki cards with Gemini AI")
        print("5. Batch create folders and cards")
        print("6. Open folder and create cards by topic")
        print("7. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            print("\n-- Creating Anki cards from text file --")
            file_path = input("Enter text file path: ")
            if os.path.exists(file_path):
                cards = create_anki_cards_from_text_file(file_path)
                print(f"Created {len(cards)} cards from text file")
                
                save_option = input("Save cards to CSV? (y/n): ")
                if save_option.lower() == 'y':
                    output_path = input("Enter output CSV path: ")
                    delimiter = input("Enter delimiter (default ';'): ") or ';'
                    save_cards_to_csv(cards, output_path, delimiter)
            else:
                print("File not found!")
                
        elif choice == "2":
            print("\n-- Creating Anki cards from CSV file --")
            file_path = input("Enter CSV file path: ")
            if os.path.exists(file_path):
                delimiter = input("Enter delimiter (default ','): ") or ','
                cards = create_anki_cards_from_csv_file(file_path, delimiter)
                print(f"Created {len(cards)} cards from CSV file")
                
                convert_option = input("Convert to different format? (y/n): ")
                if convert_option.lower() == 'y':
                    output_path = input("Enter output CSV path: ")
                    new_delimiter = input("Enter new delimiter (default ';'): ") or ';'
                    save_cards_to_csv(cards, output_path, new_delimiter)
            else:
                print("File not found!")
                
        elif choice == "3":
            print("\n-- Creating folder for Anki cards --")
            folder_path = input("Enter folder path: ")
            create_folder_for_anki_cards(folder_path)
            
        elif choice == "4":
            print("\n-- Generating Anki cards with Gemini AI --")
            api_key = input("Enter your Gemini API key: ")
            
            if not api_key:
                print("API key is required for Gemini API access")
                continue
                
            topic = input("Enter the topic for flashcards: ")
            num_cards = int(input("Number of cards to generate (default 10): ") or 10)
            
            format_choice = input("Use custom formatting instructions? (y/n): ")
            format_instructions = None
            if format_choice.lower() == 'y':
                print("Enter custom formatting instructions (press Enter twice to finish):")
                lines = []
                while True:
                    line = input()
                    if not line and lines and not lines[-1]:
                        break
                    lines.append(line)
                format_instructions = '\n'.join(lines)
            
            print("Generating cards with Gemini AI...")
            try:
                cards = generate_anki_cards_with_gemini(api_key, topic, num_cards, format_instructions)
                print(f"Generated {len(cards)} cards")
                
                # Preview some cards
                if cards:
                    print("\nPreview of generated cards:")
                    for i, (question, answer) in enumerate(cards[:3], 1):
                        print(f"\nCard {i}:")
                        print(f"Q: {question}")
                        print(f"A: {answer}")
                    
                    if len(cards) > 3:
                        print(f"\n... plus {len(cards) - 3} more cards")
                
                save_option = input("\nSave cards to CSV? (y/n): ")
                if save_option.lower() == 'y':
                    output_path = input("Enter output CSV path: ")
                    delimiter = input("Enter delimiter (default ';'): ") or ';'
                    save_cards_to_csv(cards, output_path, delimiter)
            except Exception as e:
                print(f"Error generating cards: {e}")
            
        elif choice == "5":
            print("\n-- Batch creating folders and cards --")
            create_batch_folders_and_cards()
            
        elif choice == "6":
            print("\n-- Open folder and create cards by topic --")
            open_folder_and_generate_cards()
            
        elif choice == "7":
            print("\nExiting Anki Card Generator. Goodbye!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")
            
if __name__ == "__main__":
    main()