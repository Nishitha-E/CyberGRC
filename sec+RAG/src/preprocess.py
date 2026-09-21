import re

def clean_text(text: str) -> str:
    """Clean and normalize text content for embedding and comparison."""
    if not text:
        return ""
    # Normalize unicode whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()

def normalize_control_id(control_id: str) -> str:
    """Normalize control ID formats (e.g., 'ac-2' -> 'AC-2')."""
    if not control_id:
        return "N/A"
    return control_id.strip().upper()
