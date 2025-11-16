# database_matches.py
from pathlib import Path
import json

BASE_FILE = Path(__file__).resolve().parent / "matches.json"

# --------------------------
# Save a new match to log
# --------------------------
def save_match_record(founder_email: str, designer_email: str, score: float):
    record = {
        "founder": founder_email,
        "designer": designer_email,
        "score": score
    }

    # If file doesn't exist, create it
    if not BASE_FILE.exists():
        with open(BASE_FILE, "w") as f:
            json.dump([], f, indent=2)

    # Load existing
    with open(BASE_FILE, "r") as f:
        data = json.load(f)

    # Add new record
    data.append(record)

    # Save back
    with open(BASE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --------------------------
# Read all match logs
# --------------------------
def get_all_match_records():
    if not BASE_FILE.exists():
        return []

    with open(BASE_FILE, "r") as f:
        return json.load(f)
