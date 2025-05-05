import json
import re
from typing import List, Tuple, Optional

# Import the official Google Generative AI Python client library
try:
    import google.generativeai as genai
except ImportError:
    print("Google Generative AI library not found. Please install it with:")
    print("pip install google-generativeai")
    raise


def generate_anki_cards_with_gemini(
    api_key: str, 
    topic: str, 
    num_cards: int = 10, 
    format_instructions: Optional[str] = None
) -> List[Tuple[str, str]]:
    """
    Generate Anki cards using Google's Gemini AI API.
    
    Args:
        api_key: Google API key with Gemini access
        topic: The topic to generate cards for
        num_cards: Number of cards to generate (default: 10)
        format_instructions: Optional specific formatting instructions
        
    Returns:
        List of tuples containing (question, answer) pairs
    """
    if not api_key:
        raise ValueError("API key is required for Gemini API access")
    
    # Configure the Gemini API client
    genai.configure(api_key=api_key)
    
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
    
    # Get a reference to the model
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Generate the content
    try:
        response = model.generate_content(prompt)
        
        # Process the response text
        response_text = response.text
        
        # First try to parse as JSON
        cards = _try_parse_json(response_text)
        if cards is not None:
            return cards
        
        # If JSON parsing fails, try to extract cards from text
        return _extract_cards_from_text(response_text)
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return []


def _try_parse_json(text: str) -> Optional[List[Tuple[str, str]]]:
    """
    Try to parse JSON content from the AI response.
    
    Args:
        text: Text from the AI response
    
    Returns:
        List of tuples containing (question, answer) pairs or None if parsing fails
    """
    # Find JSON content - look for JSON array
    json_start = text.find('[')
    json_end = text.rfind(']') + 1
    
    if json_start == -1 or json_end == 0:
        # Try to find JSON object if not an array
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
    
    if json_start >= 0 and json_end > json_start:
        json_content = text[json_start:json_end]
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
            return None
    
    return None


def _extract_cards_from_text(text: str) -> List[Tuple[str, str]]:
    """
    Extract flashcards from text if JSON parsing fails.
    
    Args:
        text: Text from the AI response
        
    Returns:
        List of tuples containing (question, answer) pairs
    """
    cards = []
    lines = text.split('\n')
    
    # Pattern for question indicators
    q_pattern = re.compile(r'^(?:Q:|Question:|Q\.\s*|Card\s*\d+:|^\d+\)|^\d+\.)')
    # Pattern for answer indicators
    a_pattern = re.compile(r'^(?:A:|Answer:|A\.\s*)')
    
    current_question = None
    current_answer = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a question line
        q_match = q_pattern.search(line)
        if q_match:
            # Save the previous card if it exists
            if current_question and current_answer:
                cards.append((current_question, ' '.join(current_answer)))
                current_answer = []
            
            # Extract the question text by removing the prefix
            prefix_end = q_match.end()
            current_question = line[prefix_end:].strip()
            continue
        
        # Check if this is an answer line
        a_match = a_pattern.search(line)
        if a_match and current_question:
            # Extract the answer text by removing the prefix
            prefix_end = a_match.end()
            answer_text = line[prefix_end:].strip()
            current_answer.append(answer_text)
            continue
        
        # If we already have a question and are collecting the answer
        if current_question and (current_answer or a_match):
            current_answer.append(line)
    
    # Don't forget to add the last card
    if current_question and current_answer:
        cards.append((current_question, ' '.join(current_answer)))
    
    return cards