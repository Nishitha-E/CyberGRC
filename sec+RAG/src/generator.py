import os
from typing import Dict, Any

def get_generation_mode() -> str:
    """Detect available generation mode based on environment setup."""
    if os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"):
        return "LLM-assisted"
    return "Evidence-only"

def generate_report(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates evidence-grounded response and remediation recommendations.
    Uses Evidence-only mode (deterministiccontext synthesis) or optional LLM-assisted mode.
    """
    mode = get_generation_mode()
    
    if analysis_result["status"] == "NO_EVIDENCE":
        return {
            "generation_mode": mode,
            "has_evidence": False,
            "explanation": analysis_result["message"],
            "control_relevance": [],
            "remediations": [],
            "markdown_report": f"### Assessment Result\n\n**{analysis_result['message']}**"
        }

    finding = analysis_result["finding"]
    risk = analysis_result["risk_info"]
    passed_docs = analysis_result["passed_docs"]
    
    # 1. Deterministic Evidence-Only Synthesis
    explanation = (
        f"The reported security finding indicates operational control gaps regarding "
        f"**{', '.join(analysis_result['frameworks'])}** security requirements. "
        f"Based on the transparent risk model, this issue presents a **{risk['level']} Risk** "
        f"(Impact: {risk['impact']}/5, Likelihood: {risk['likelihood']}/5, Score: {risk['score']}/25)."
    )

    control_relevances = []
    for doc in passed_docs:
        control_relevances.append({
            "framework": doc["framework"],
            "control_id": doc["control_id"],
            "title": doc["title"],
            "similarity": doc["similarity_score"],
            "summary": doc["content"]
        })

    remediations = analysis_result["remediations"]

    # Build clean markdown synthesis report
    report_lines = [
        f"### Security Assessment Prototype Report",
        f"**Generation Mode**: `{mode}` | **Status**: `Evidence Grounded`",
        "",
        f"#### 1. Executive Summary & Finding Analysis",
        f"{explanation}",
        "",
        f"#### 2. Control Gap & Compliance Analysis",
    ]
    
    for gap in analysis_result["gaps"]:
        report_lines.append(f"- {gap}")
        
    report_lines.extend([
        "",
        f"#### 3. Recommended Remediation Actions (Retrieved Evidence Grounded)",
    ])
    
    for idx, rem in enumerate(remediations, 1):
        report_lines.append(f"{idx}. {rem}")
        
    report_lines.extend([
        "",
        f"#### 4. Authoritative Control References",
    ])
    
    for doc in passed_docs:
        report_lines.append(
            f"- **{doc['framework']} - {doc['control_id']}**: *{doc['title']}* (Relevance Score: {doc['similarity_score']:.2f})"
        )

    markdown_report = "\n".join(report_lines)

    return {
        "generation_mode": mode,
        "has_evidence": True,
        "explanation": explanation,
        "control_relevance": control_relevances,
        "remediations": remediations,
        "markdown_report": markdown_report
    }
