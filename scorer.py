
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# score_url(url: str) -> dict
# Purpose:
#   Evaluate a URL with simple, explainable heuristics and return a score
#   in [0,1] plus a human-readable explanation string. This mirrors D1.
# Inputs:
#   url (str): candidate URL to evaluate.
# Outputs:
#   dict with keys: {"score": float, "explanation": str}
# ---------------------------------------------------------------------------
def score_url(url: str) -> dict:
    p = urlparse(url)
    score = 0.5   # start neutral; clamp later
    reasons = []

    # --- Scheme heuristic: prefer HTTPS for transport security (not credibility per se,
    #     but a common signal of basic site hygiene). Adds +0.10 for https,
    #     -0.05 for http; 0 if unknown/other.
    if p.scheme == "https":
        score += 0.10
        reasons.append("HTTPS bonus (+0.10)")
    elif p.scheme == "http":
        score -= 0.05
        reasons.append("HTTP penalty (-0.05)")

    # --- TLD heuristic: educational/government TLDs tend to be more controlled.
    #     This is *not* a guarantee of truthfulness; it’s a prior.
    if any(p.netloc.endswith(t) for t in (".edu", ".gov", ".int")):
        score += 0.10
        reasons.append("High-trust TLD (+0.10)")

    # --- Path depth heuristic: very deep paths can sometimes indicate low-quality
    #     content routing. Keep penalty mild to avoid false negatives.
    depth = len([s for s in p.path.split("/") if s])
    if depth > 3:
        score -= 0.05
        reasons.append("Deep path (-0.05)")

    # --- Clamp and format explanation
    score = max(0.0, min(1.0, score))
    explanation = "; ".join(reasons) if reasons else "Neutral baseline"
    return {"score": round(score, 3), "explanation": explanation}
