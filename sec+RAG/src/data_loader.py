import os
import re
from typing import List, Dict, Any
from datasets import load_dataset
from src.config import HUGGINGFACE_DATASET
from src.preprocess import clean_text, normalize_control_id

def extract_title_from_instruction(instruction: str, framework: str) -> str:
    """Extract clean concise title from instruction text."""
    if not instruction:
        return "Control Requirement"
    # Remove standard prompt prefix questions
    title = re.sub(r'^(What are the requirements for|Describe|Explain|What is the control for)\s+', '', instruction, flags=re.IGNORECASE)
    title = re.sub(r'\s+(according to|under|in)\s+.*$', '', title, flags=re.IGNORECASE)
    title = title.strip().rstrip('?')
    return title if title else instruction

def load_and_normalize_dataset() -> List[Dict[str, Any]]:
    """
    Loads Zeezhu/grc-security-frameworks dataset (alpaca split),
    normalizes to standard schema, removes duplicate controls,
    and returns list of clean document dicts.
    """
    print(f"[DATA LOADER] Loading dataset '{HUGGINGFACE_DATASET}' (config: 'alpaca')...")
    raw_ds = load_dataset(HUGGINGFACE_DATASET, "alpaca", split="train")
    
    documents = []
    seen_keys = set()
    dup_count = 0
    
    for idx, item in enumerate(raw_ds):
        framework = clean_text(item.get("source", "GRC Framework"))
        control_id = normalize_control_id(item.get("id", f"CTRL-{idx}"))
        output_text = clean_text(item.get("output", ""))
        instruction_text = clean_text(item.get("instruction", ""))
        
        if not output_text:
            continue
            
        title = extract_title_from_instruction(instruction_text, framework)
        
        # Deduplication key based on framework + control_id + content snippet
        dedup_key = f"{framework}::{control_id}::{output_text[:100].lower()}"
        if dedup_key in seen_keys:
            dup_count += 1
            continue
        seen_keys.add(dedup_key)
        
        # Rich search text for embedding vector
        search_text = f"Framework: {framework} | Control: {control_id} | Title: {title}\nDescription: {output_text}"
        
        doc = {
            "doc_id": f"doc_{len(documents)}",
            "framework": framework,
            "control_id": control_id,
            "title": title,
            "content": output_text,
            "instruction": instruction_text,
            "source": framework,
            "document_type": "security_control",
            "search_text": search_text
        }
        documents.append(doc)
        
    print(f"[DATA LOADER] Loaded {len(raw_ds)} raw records.")
    print(f"[DATA LOADER] Deduplicated {dup_count} duplicate items.")
    print(f"[DATA LOADER] Total unique GRC control documents: {len(documents)}")
    
    return documents
