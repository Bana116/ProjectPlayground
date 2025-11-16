# match.py
from .database import get_all_designers, format_designer, format_founder


# -------------------------------
# Helpers to normalize values
# -------------------------------
def _norm_list(value):
    """
    Converts lists or comma-separated strings into
    a clean, lowercase Python list.
    """
    if not value:
        return []

    if isinstance(value, list):
        return [v.strip().lower() for v in value if v]

    return [v.strip().lower() for v in str(value).split(",") if v]


def _norm_str(value):
    """
    Converts any value to a clean, lowercase string.
    """
    return (value or "").strip().lower()


# -------------------------------
# Scoring Engine
# -------------------------------
def compute_match_score(founder, designer):
    """
    Returns a score between 0 and 1 for how well this designer
    matches this founder. You can tune this later.
    """

    score = 0
    max_score = 0

    # 1) Niche overlap — FIXED to handle lists correctly
    founder_niches = _norm_list(founder.get("niche"))
    designer_niches = _norm_list(designer.get("niche_interest"))
    max_score += 3

    if founder_niches and designer_niches:
        if any(n in designer_niches for n in founder_niches):
            score += 3

    # 2) Beginner friendly preference
    beginner = founder.get("beginner_friendly")
    max_score += 2
    if beginner == "Yes":
        score += 1

    # 3) Tool overlap
    founder_tools = _norm_list(founder.get("tools_used"))
    designer_tools = _norm_list(designer.get("tools"))
    max_score += 3

    if founder_tools and designer_tools:
        overlap = len(set(founder_tools) & set(designer_tools))
        score += min(overlap, 3)

    # 4) Support level ↔ availability (very light weighting)
    max_score += 2
    founder_support = founder.get("support_level")
    designer_availability = designer.get("availability")

    if founder_support and designer_availability:
        score += 1

    if max_score == 0:
        return 0.0

    return round(score / max_score, 3)


# -------------------------------
# Best-match helper (optional)
# -------------------------------
def find_best_designer_for_founder(founder_row):
    """
    founder_row is a raw DB row (tuple).
    We convert it to a dict via format_founder().
    Returns:
        (designer_dict, score)
    Or:
        (None, 0)
    """

    founder = format_founder(founder_row)

    designers_rows = get_all_designers()
    if not designers_rows:
        return None, 0.0

    scored = []
    for row in designers_rows:
        designer = format_designer(row)
        s = compute_match_score(founder, designer)
        scored.append((s, designer))

    # highest score first
    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_designer = scored[0]

    if best_score <= 0:
        return None, 0.0

    return best_designer, best_score
