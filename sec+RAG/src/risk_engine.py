from typing import Dict, Any, Tuple

def calculate_risk(impact: int, likelihood: int) -> Dict[str, Any]:
    """
    Calculates transparent risk score and risk level classification.
    
    Formula: Risk Score = Impact (1-5) * Likelihood (1-5)
    Range: 1 - 25
    Classification:
        1 - 4: LOW
        5 - 9: MEDIUM
        10 - 16: HIGH
        17 - 25: CRITICAL
    """
    # Clamp values between 1 and 5
    impact = max(1, min(5, int(impact)))
    likelihood = max(1, min(5, int(likelihood)))
    
    score = impact * likelihood
    
    if score <= 4:
        level = "LOW"
        color = "#28a745"  # Green
        badge_bg = "rgba(40, 167, 69, 0.2)"
    elif score <= 9:
        level = "MEDIUM"
        color = "#ffc107"  # Yellow
        badge_bg = "rgba(255, 193, 7, 0.2)"
    elif score <= 16:
        level = "HIGH"
        color = "#fd7e14"  # Orange
        badge_bg = "rgba(253, 126, 20, 0.2)"
    else:
        level = "CRITICAL"
        color = "#dc3545"  # Red
        badge_bg = "rgba(220, 53, 69, 0.2)"
        
    return {
        "impact": impact,
        "likelihood": likelihood,
        "score": score,
        "level": level,
        "color": color,
        "badge_bg": badge_bg,
        "disclaimer": "This is a demonstration risk model and does not replace an organization's formal risk methodology."
    }
