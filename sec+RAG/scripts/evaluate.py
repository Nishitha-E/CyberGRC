import sys
import time
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retriever import GRCRetriever
from src.analyzer import analyze_finding
from src.generator import generate_report

TEST_QUERIES = [
    {
        "id": 1,
        "query": "Administrative accounts do not use MFA.",
        "category": "Identity & Access Control",
    },
    {
        "id": 2,
        "query": "Security logs are not centrally monitored.",
        "category": "Logging & Monitoring",
    },
    {
        "id": 3,
        "query": "Employees have excessive privileges.",
        "category": "Least Privilege / Access Control",
    },
    {
        "id": 4,
        "query": "Sensitive data is not encrypted.",
        "category": "Cryptography / Data Security",
    },
    {
        "id": 5,
        "query": "Organization does not maintain an asset inventory.",
        "category": "Asset Management",
    },
    {
        "id": 6,
        "query": "Cloud storage is publicly accessible.",
        "category": "Cloud Security / Access Control",
    },
    {
        "id": 7,
        "query": "I want a recipe for chocolate cake.",
        "category": "Negative Test (Irrelevant Query)",
    }
]

def run_evaluation():
    print("==========================================================================================")
    print("  CyberGRC - Automated Evaluation & Performance Benchmark Suite")
    print("==========================================================================================")
    
    retriever = GRCRetriever()
    if not retriever.is_indexed():
        print("[ERROR] Vector index not initialized. Please run 'python scripts/build_index.py' first.")
        sys.exit(1)

    print(f"Total documents in vector index: {retriever.document_count()}")
    
    # Warm-up call so initial PyTorch / Transformer initialization isn't counted in query timing
    print("[BENCHMARK] Warming up embedding model & vector database...")
    _ = retriever.retrieve("warmup query", top_k=1)
    print("[BENCHMARK] Warm-up complete. Running evaluation suite...\n")

    results = []
    
    for item in TEST_QUERIES:
        q_id = item["id"]
        query = item["query"]
        cat = item["category"]
        
        # Default impact=4, likelihood=4 for test risk scoring
        retrieval_res = retriever.retrieve(query, top_k=3, threshold=0.35)
        analysis_res = analyze_finding(query, impact=4, likelihood=4, retrieval_result=retrieval_res)
        report = generate_report(analysis_res)
        
        passed = analysis_res["passed_docs"]
        latency = retrieval_res["retrieval_time_ms"]
        status = analysis_res["status"]
        
        ctrl_str = ", ".join([f"{d['framework']} {d['control_id']}" for d in passed]) if passed else "None"
        max_score = max([d['similarity_score'] for d in retrieval_res['retrieved_docs']]) if retrieval_res['retrieved_docs'] else 0.0
        
        # Verify negative test behavior
        if q_id == 7:
            negative_pass = (status == "NO_EVIDENCE") and ("No sufficiently relevant security control" in analysis_res["message"])
            status_display = "PASSED (NO EVIDENCE)" if negative_pass else "FAILED (FALSE POSITIVE)"
        else:
            status_display = f"EVIDENCE FOUND ({len(passed)} controls)" if status == "EVIDENCE_FOUND" else "NO EVIDENCE"

        results.append({
            "id": q_id,
            "category": cat,
            "query": query,
            "latency_ms": latency,
            "status": status_display,
            "top_controls": ctrl_str,
            "top_similarity": max_score
        })

    # Print summary table
    print(f"{'ID':<3} | {'Category':<32} | {'Latency':<9} | {'Max Sim':<7} | {'Status':<22} | {'Retrieved Controls'}")
    print("-" * 110)
    
    total_latency = 0.0
    for r in results:
        total_latency += r["latency_ms"]
        print(f"{r['id']:<3} | {r['category']:<32} | {r['latency_ms']:>6.2f} ms | {r['top_similarity']:>6.4f} | {r['status']:<22} | {r['top_controls']}")
        
    avg_latency = total_latency / len(results)
    print("-" * 110)
    print(f"Average Retrieval Latency: {avg_latency:.2f} ms (Target: < 1000.00 ms)")
    print("Evaluation completed successfully!\n")

if __name__ == "__main__":
    run_evaluation()
