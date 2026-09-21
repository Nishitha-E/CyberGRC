from typing import Dict, Any, List
from src.config import NO_EVIDENCE_MESSAGE
from src.risk_engine import calculate_risk

def analyze_finding(
    finding_text: str,
    impact: int,
    likelihood: int,
    retrieval_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyzes user cybersecurity finding against retrieved GRC controls.
    Combines risk calculation, control gap identification, and evidence formatting.
    """
    risk_info = calculate_risk(impact, likelihood)
    
    has_evidence = retrieval_result.get("has_evidence", False)
    passed_docs = retrieval_result.get("passed_docs", [])
    retrieval_time_ms = retrieval_result.get("retrieval_time_ms", 0.0)
    total_searched = retrieval_result.get("total_searched", 0)
    
    if not has_evidence:
        return {
            "status": "NO_EVIDENCE",
            "message": NO_EVIDENCE_MESSAGE,
            "risk_info": risk_info,
            "finding": finding_text,
            "retrieval_time_ms": retrieval_time_ms,
            "total_searched": total_searched,
            "retrieved_docs": retrieval_result.get("retrieved_docs", []),
            "passed_docs": []
        }

    # Extract primary frameworks and control IDs from passed evidence
    frameworks = sorted(list(set(d["framework"] for d in passed_docs)))
    control_ids = [d["control_id"] for d in passed_docs]
    
    # Synthesize control gaps and remediation actions directly from retrieved content
    gaps = []
    remediations = []
    
    for doc in passed_docs:
        ctrl = doc["control_id"]
        title = doc["title"]
        fw = doc["framework"]
        content = doc["content"]
        
        gaps.append(f"**{fw} ({ctrl} - {title})**: Current practice fails to satisfy requirement: '{content[:180]}...'")
        
        # Build concise actionable remediation from requirement content
        remediations.append(f"Implement requirements under **{fw} {ctrl}**: {content}")

    return {
        "status": "EVIDENCE_FOUND",
        "message": "Relevant security controls retrieved successfully.",
        "risk_info": risk_info,
        "finding": finding_text,
        "frameworks": frameworks,
        "control_ids": control_ids,
        "gaps": gaps,
        "remediations": remediations,
        "passed_docs": passed_docs,
        "retrieved_docs": retrieval_result.get("retrieved_docs", []),
        "retrieval_time_ms": retrieval_time_ms,
        "total_searched": total_searched
    }
