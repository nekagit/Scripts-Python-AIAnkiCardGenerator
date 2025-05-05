import os
import tkinter as tk
from tkinter import filedialog

from anki_utils import (
    create_folder_for_anki_cards,
    create_anki_cards_from_text_file,
    save_cards_to_csv
)
from gemini_generator import generate_anki_cards_with_gemini


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
    import time
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
    
    # Choose generation method
    print("\nHow would you like to generate cards?")
    print("1. Empty placeholder cards")
    print("2. Generate with Gemini AI")
    gen_choice = input("Enter choice (1-2): ")
    
    api_key = None
    if gen_choice == "2":
        api_key = input("Enter your Gemini API key: ")
        if not api_key:
            print("API key is required for Gemini. Falling back to empty cards.")
            gen_choice = "1"
    
    for folder in folders:
        # Create folder
        folder_path = os.path.join(base_dir, folder)
        create_folder_for_anki_cards(folder_path)
        
        # Generate cards
        cards = []
        if gen_choice == "2":
            try:
                print(f"\nGenerating cards for '{folder}'...")
                cards = generate_anki_cards_with_gemini(api_key, folder, cards_per_folder)
                print(f"Generated {len(cards)} cards for '{folder}'")
            except Exception as e:
                print(f"Error generating cards for '{folder}': {e}")
        
        # Save cards
        csv_path = os.path.join(folder_path, f"{folder}_cards.csv")
        save_cards_to_csv(cards, csv_path, delimiter=';')
    
    print(f"\nCreated {len(folders)} folders with card files.")


def main():
    print("\n===== Anki Card Generator =====")
    print("This script helps create and manage Anki cards")
    
    while True:
        print("\nChoose Menu Options:")
        print("1. Create Anki cards from text file")
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