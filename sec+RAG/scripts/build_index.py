import sys
import time
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_and_normalize_dataset
from src.retriever import GRCRetriever
from src.config import EMBEDDING_MODEL_NAME, VECTORSTORE_DIR

def main():
    print("==================================================")
    print("  CyberGRC - Vector Index Builder")
    print("==================================================")
    start_total = time.perf_counter()

    # 1. Load and normalize dataset
    documents = load_and_normalize_dataset()

    if not documents:
        print("[ERROR] No valid documents retrieved from dataset.")
        sys.exit(1)

    # 2. Build ChromaDB Vector Index ONCE
    print(f"\n[BUILD] Initializing vector retriever at: {VECTORSTORE_DIR}")
    retriever = GRCRetriever()
    
    build_stats = retriever.build_index(documents)

    total_time = round(time.perf_counter() - start_total, 2)

    print("\n--------------------------------------------------")
    print("  BUILD SUMMARY & INDEX STATISTICS")
    print("--------------------------------------------------")
    print(f"Controls Indexed:    {build_stats['documents_indexed']}")
    print(f"Embedding Model:     {EMBEDDING_MODEL_NAME}")
    print(f"Index Location:      {build_stats['index_path']}")
    print(f"Index Build Time:    {build_stats['build_time_seconds']} seconds")
    print(f"Total Pipeline Time: {total_time} seconds")
    print("--------------------------------------------------")
    print("SUCCESS: Index built successfully! Vector index persisted to disk.")
    print("Ready to launch Streamlit application: streamlit run app.py\n")

if __name__ == "__main__":
    main()
