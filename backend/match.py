# match.py
from database import get_all_designers, format_designer, format_founder

# tiny helpers so we don’t crash on None
def _norm_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return [v.strip().lower() for v in value if v]
    return [v.strip().lower() for v in str(value).split(",") if v]

def _norm_str(value):
    return (value or "").strip().lower()


def compute_match_score(founder, designer):
    """
    Returns a score between 0 and 1 for how well this designer matches this founder.
    You can tune this later – this is your 'ML-ish' brain.
    """

    score = 0
    max_score = 0

    # 1) Niche / domain overlap
    founder_niche = _norm_str(founder.get("niche"))
    designer_niches = _norm_list(designer.get("niche_interest"))
    max_score += 3
    if founder_niche and designer_niches and founder_niche in designer_niches:
        score += 3

    # 2) Beginner-friendly vs designer experience goals
    beginner = founder.get("beginner_friendly")
    max_score += 2
    if beginner == "Yes":
        score += 1

    # 3) Tools overlap
    founder_tools = _norm_list(founder.get("tools_used"))
    designer_tools = _norm_list(designer.get("tools"))
    max_score += 3
    if founder_tools and designer_tools:
        overlap = len(set(founder_tools) & set(designer_tools))
        score += min(overlap, 3)

    # 4) Availability / support level (super rough for now)
    max_score += 2
    if founder.get("support_level") and designer.get("availability"):
        score += 1  # just a small bump

    if max_score == 0:
        return 0.0

    return round(score / max_score, 3)


def find_best_designer_for_founder(founder_row):
    """
    founder_row is the raw DB row (tuple). We convert it to dict via format_founder.
    Returns (designer_dict, score) or (None, 0).
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

    # sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_designer = scored[0]

    # You can require a minimum score if you want
    if best_score <= 0:
        return None, 0.0

    return best_designer, best_score
