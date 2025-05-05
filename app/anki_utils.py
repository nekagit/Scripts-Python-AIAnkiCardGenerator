import os
import csv
from typing import List, Tuple


def create_anki_cards_from_text_file(file_path: str) -> List[Tuple[str, str]]:
    """
    Create Anki cards from a tab-separated text file.
    
    Args:
        file_path: Path to the tab-separated text file
        
    Returns:
        List of (question, answer) tuples
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    cards = []
    for line in lines:
        if '\t' in line:
            question, answer = line.strip().split('\t')
            cards.append((question, answer))
    
    return cards


def create_anki_cards_from_csv_file(file_path: str, delimiter: str = ',') -> List[Tuple[str, str]]:
    """
    Create Anki cards from a CSV file with specified delimiter.
    
    Args:
        file_path: Path to the CSV file
        delimiter: CSV delimiter character (default: ',')
        
    Returns:
        List of (question, answer) tuples
    """
    cards = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            if len(row) >= 2:
                question, answer = row[0], row[1]
                cards.append((question, answer))
    
    return cards


def create_folder_for_anki_cards(folder_path: str) -> str:
    """
    Create a folder for storing Anki cards if it doesn't exist.
    
    Args:
        folder_path: Path to create the folder
        
    Returns:
        Path to the created folder
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")
    
    return folder_path


def save_cards_to_csv(cards: List[Tuple[str, str]], file_path: str, delimiter: str = ';') -> None:
    """
    Save cards to a CSV file with specified delimiter.
    
    Args:
        cards: List of (question, answer) tuples
        file_path: Path to save the CSV file
        delimiter: CSV delimiter character (default: ';')
    """
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=delimiter)
        for card in cards:
            writer.writerow(card)
    
    print(f"Saved {len(cards)} cards to {file_path}")