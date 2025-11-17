# match.py

from .database import (
    get_all_designers,
    format_designer,
    format_founder,
)

# -----------------------------
# small helpers
# -----------------------------

def _norm_str(value):
    return (value or "").strip().lower()


def _norm_list(value):
    """
    Accepts:
      - list -> lowercased & stripped
      - comma-separated string -> split to list
      - None -> []
    """
    if not value:
        return []
    if isinstance(value, list):
        return [v.strip().lower() for v in value if v]
    return [v.strip().lower() for v in str(value).split(",") if v]


def _parse_hours(raw):
    """
    Very forgiving parser for things like:
      "3–5 hours", "2-3 hrs", "10 hours", "5"
    Returns an integer (approx average) or None.
    """
    if not raw:
        return None

    text = str(raw)
    # replace en-dash etc with hyphen
    text = text.replace("–", "-").lower()

    # extract digits
    import re
    nums = re.findall(r"\d+", text)
    if not nums:
        return None

    nums = [int(n) for n in nums]

    if len(nums) == 1:
        return nums[0]

    # if "3-5" -> average = 4
    return int(round(sum(nums) / len(nums)))


def _bucket_hours(h):
    """
    Turn raw hours number into a rough "intensity" bucket.
    """
    if h is None:
        return None
    if h <= 3:
        return "light"
    if h <= 8:
        return "medium"
    return "heavy"


# -----------------------------
# core scoring
# -----------------------------

def compute_match_score(founder: dict, designer: dict) -> float:
    """
    Returns a number between 0 and 1:
      0   = terrible / no overlap
      1.0 = extremely good match

    Factors:
      - Niche alignment
      - Design focus vs design help (skills)
      - Tools used
      - Availability + hours
    """
    score = 0.0
    max_score = 0.0

    # ---------- 1) Niche overlap (strongest signal) ----------
    founder_niches = _norm_list(founder.get("niche"))
    designer_niches = _norm_list(designer.get("niche_interest"))

    # up to 4 points
    max_score += 4
    if founder_niches and designer_niches:
        overlap = len(set(founder_niches) & set(designer_niches))
        # cap at 4
        score += min(overlap, 4)

    # ---------- 2) Skills / design focus vs needs ----------
    founder_needs = _norm_list(founder.get("design_help"))
    designer_focus = _norm_list(designer.get("focus"))

    # up to 3 points
    max_score += 3
    if founder_needs and designer_focus:
        overlap = len(set(founder_needs) & set(designer_focus))
        score += min(overlap, 3)

    # ---------- 3) Tools overlap ----------
    founder_tools = _norm_list(founder.get("tools_used"))
    designer_tools = _norm_list(designer.get("tools"))

    # up to 3 points
    max_score += 3
    if founder_tools and designer_tools:
        overlap = len(set(founder_tools) & set(designer_tools))
        score += min(overlap, 3)

    # ---------- 4) Hours & availability fit ----------
    # Founder: estimated_hours (string like "3–5 hours a week")
    founder_hours_raw = founder.get("estimated_hours")
    founder_hours_val = _parse_hours(founder_hours_raw)
    founder_bucket = _bucket_hours(founder_hours_val)

    # Designer: currently only has "availability" (Weekdays / Weekends / Evenings / Flexible)
    designer_availability = _norm_list(designer.get("availability"))

    # We treat:
    #   - more availability options = more flexible
    #   - heavy hours + no availability = bad
    #   - light hours + any availability = fine
    max_score += 3

    if founder_bucket is None:
        # no hours info; give a small neutral bump if designer is broadly available
        if len(designer_availability) >= 2:
            score += 1
    else:
        # we have some expected intensity
        if founder_bucket == "light":
            # any availability is okay
            if designer_availability:
                score += 2
        elif founder_bucket == "medium":
            # needs at least some flexibility
            if len(designer_availability) >= 2:
                score += 2
            elif designer_availability:
                score += 1
        elif founder_bucket == "heavy":
            # prefers very available designers
            if "flexible" in designer_availability:
                score += 3
            elif len(designer_availability) >= 2:
                score += 2

    # ---------- 5) Small bonus: designer actually filled niche / goals ----------
    # Encourages designers who put in more info
    max_score += 2
    info_rich = 0

    if designer_niches:
        info_rich += 1
    goals = _norm_list(designer.get("goals"))
    if goals:
        info_rich += 1

    score += info_rich  # up to +2

    # ---------- final normalization ----------
    if max_score == 0:
        return 0.0

    return round(score / max_score, 4)


# -----------------------------
# optional helper for admin use
# -----------------------------

def find_best_designer_for_founder(founder_row):
    """
    Helper used by admin tools.

    - founder_row: raw sqlite row from `founders` table
    - returns: (best_designer_dict, score) or (None, 0.0)
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

    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_designer = scored[0]
    if best_score <= 0:
        return None, 0.0

    return best_designer, best_score
