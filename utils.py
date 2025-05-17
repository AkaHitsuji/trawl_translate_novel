"""
Utility functions for the trawl-translate-novel project.
"""
import os
import re
from typing import Dict, List, Optional

def split_content(content: str, num_chunks: int = 3) -> List[str]:
    """
    Split content into manageable chunks for translation based on newlines.
    
    Args:
        content: Text content to split
        num_chunks: Number of chunks to split into
        
    Returns:
        List of content chunks
    """
    if not content:
        return []
        
    # Calculate approximate chunk size
    chunk_size = len(content) // num_chunks
    chunks = []
    
    # Create more precise split points at newlines
    start_idx = 0
    for i in range(1, num_chunks):
        # Find the nearest newline after the calculated split point
        target_idx = start_idx + chunk_size
        if target_idx >= len(content):
            break
            
        # Look for newline from the target index
        split_idx = content.find('\n', target_idx)
        if split_idx == -1:
            # If no newline found, use the target index
            split_idx = target_idx
        else:
            # Include the newline in the chunk
            split_idx += 1
            
        # Add the chunk
        chunks.append(content[start_idx:split_idx])
        start_idx = split_idx
    
    # Add the final chunk
    if start_idx < len(content):
        chunks.append(content[start_idx:])
    
    return chunks

def combine_content(chunks: List[str]) -> str:
    """
    Combine content chunks back into a single string.
    
    Args:
        chunks: List of content chunks
        
    Returns:
        Combined content
    """
    return "".join(chunks)

def load_translated_titles(filepath: str) -> Dict[str, str]:
    """
    Load translated titles from a file.
    
    Args:
        filepath: Path to the file containing translated titles
        
    Returns:
        Dictionary mapping chapter numbers to translated titles
    """
    translated_titles = {}
    
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if '_' in line:
                    details = line.split("_", 1)
                    translated_titles[details[0]] = line.strip()
    except IOError as e:
        print(f"Error loading translated titles from {filepath}: {str(e)}")
    
    return translated_titles

def get_translated_title(chapter_num: str, translated_titles: Dict[str, str]) -> str:
    """
    Get a translated title for a chapter number.
    
    Args:
        chapter_num: Chapter number to look up
        translated_titles: Dictionary of translated titles
        
    Returns:
        Translated title
        
    Raises:
        ValueError: If chapter number is not found in translated titles
    """
    title = translated_titles.get(chapter_num)
    if title is None:
        raise ValueError(f"Unable to find chapter {chapter_num} in translated titles")
    return title

def validate_chapter_range(
    chapter_titles: Dict[str, any], 
    starting_chapter_num: Optional[str], 
    ending_chapter_num: Optional[str]
) -> None:
    """
    Validate the starting and ending chapter numbers.
    
    Args:
        chapter_titles: Dictionary of chapter titles
        starting_chapter_num: Starting chapter number (optional)
        ending_chapter_num: Ending chapter number (optional)
        
    Raises:
        ValueError: If chapter numbers are invalid
    """
    if (
        starting_chapter_num is not None
        and chapter_titles.get(starting_chapter_num) is None
    ):
        raise ValueError(f"Chapter number {starting_chapter_num} not found in the book")
    
    if (
        ending_chapter_num is not None
        and chapter_titles.get(ending_chapter_num) is None
    ):
        raise ValueError(f"Chapter number {ending_chapter_num} not found in the book")

def format_filename(filename: str) -> str:
    """
    Format a string to be safe for use as a filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace problematic characters
    safe_filename = filename.replace("/", "-").replace(":", "_").replace("?", "")
    
    # Remove other illegal characters
    safe_filename = re.sub(r'[<>"|*]', '', safe_filename)
    
    return safe_filename

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    if directory_path and not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)

def extract_chapter_number(title: str, pattern: str = "Chapter (\d+)") -> int:
    """
    Extract chapter number from a chapter title.
    
    Args:
        title: Chapter title
        pattern: Regex pattern for chapter number
        
    Returns:
        Chapter number as int, or 0 if not found
    """
    match = re.search(pattern, title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0 