import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

# Dataset & RAG Configuration
HUGGINGFACE_DATASET = "Zeezhu/grc-security-frameworks"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_TOP_K = 3
RELEVANCE_THRESHOLD = 0.35  # Cosine similarity threshold for evidence acceptance

# Vector Collection Name
CHROMA_COLLECTION_NAME = "grc_controls"

# Risk Engine Thresholds
RISK_LEVEL_MAP = {
    (1, 4): ("LOW", "#28a745"),
    (5, 9): ("MEDIUM", "#ffc107"),
    (10, 16): ("HIGH", "#fd7e14"),
    (17, 25): ("CRITICAL", "#dc3545"),
}

NO_EVIDENCE_MESSAGE = "No sufficiently relevant security control was retrieved. Please refine the finding."
