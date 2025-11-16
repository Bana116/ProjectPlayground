import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "matcher.db"


# -----------------------------
# INIT: Create tables if missing
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Designers table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS designers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT,
        city_country TEXT,
        portfolio TEXT,
        availability TEXT,
        focus TEXT,
        interest_areas TEXT,
        unpaid_experience TEXT,
        goals TEXT,
        niche_interest TEXT,
        tools TEXT,
        figma_experience TEXT,
        resources TEXT,
        extra_notes TEXT,
        newsletter TEXT
    )
    """)

    # Founders table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS founders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT,
        project_name TEXT,
        website TEXT,
        project_stage TEXT,
        design_help TEXT,
        tools_used TEXT,
        paid_role TEXT,
        niche TEXT,
        estimated_hours TEXT,
        beginner_friendly TEXT,
        support_level TEXT,
        extra_notes TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# SAVE DESIGNER
# -----------------------------
def save_designer(data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO designers (
            full_name, email, city_country, portfolio,
            availability, focus, interest_areas,
            unpaid_experience, goals, niche_interest,
            tools, figma_experience, resources,
            extra_notes, newsletter
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["full_name"],
        data["email"],
        data["city_country"],
        data["portfolio"],
        ",".join(data["availability"]),
        ",".join(data["focus"]),
        ",".join(data["interest_areas"]),
        ",".join(data["unpaid_experience"]),
        ",".join(data["goals"]),
        ",".join(data["niche_interest"]),
        ",".join(data["tools"]),
        ",".join(data["figma_experience"]),
        ",".join(data["resources"]),
        data["extra_notes"],
        data["newsletter"]
    ))

    conn.commit()
    conn.close()


# -----------------------------
# SAVE FOUNDER
# -----------------------------
def save_founder(data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO founders (
            full_name, email, project_name, website,
            project_stage, design_help, tools_used,
            paid_role, niche, estimated_hours,
            beginner_friendly, support_level, extra_notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["full_name"],
        data["email"],
        data["project_name"],
        data["website"],
        ",".join(data["project_stage"]),
        ",".join(data["design_help"]),
        data["tools_used"],
        ",".join(data["paid_role"]),
        ",".join(data["niche"]),
        data["estimated_hours"],
        data["beginner_friendly"],
        ",".join(data["support_level"]),
        data["extra_notes"]
    ))

    conn.commit()
    conn.close()


# -----------------------------
# FETCH ALL
# -----------------------------
def get_all_designers():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM designers")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_founders():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM founders")
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------
# FORMAT DESIGNER (sqlite row → dict)
# ---------------------------
def format_designer(row):
    return {
        "id": row[0],
        "full_name": row[1],
        "email": row[2],
        "city_country": row[3],
        "portfolio": row[4],
        "availability": row[5].split(",") if row[5] else [],
        "focus": row[6].split(",") if row[6] else [],
        "interest_areas": row[7].split(",") if row[7] else [],
        "unpaid_experience": row[8].split(",") if row[8] else [],
        "goals": row[9].split(",") if row[9] else [],
        "niche_interest": row[10].split(",") if row[10] else [],
        "tools": row[11].split(",") if row[11] else [],
        "figma_experience": row[12].split(",") if row[12] else [],
        "resources": row[13].split(",") if row[13] else [],
        "extra_notes": row[14],
        "newsletter": row[15]
    }


# ---------------------------
# FORMAT FOUNDER
# ---------------------------
def format_founder(row):
    return {
        "id": row[0],
        "full_name": row[1],
        "email": row[2],
        "project_name": row[3],
        "website": row[4],
        "project_stage": row[5].split(",") if row[5] else [],
        "design_help": row[6].split(",") if row[6] else [],
        "tools_used": row[7],
        "paid_role": row[8].split(",") if row[8] else [],
        "niche": row[9].split(",") if row[9] else [],
        "estimated_hours": row[10],
        "beginner_friendly": row[11],
        "support_level": row[12].split(",") if row[12] else [],
        "extra_notes": row[13]
    }


# ---------------------------
# GET FOUNDER BY ID
# ---------------------------
def get_founder_by_id(founder_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM founders WHERE id = ?", (founder_id,))
    row = cur.fetchone()
    conn.close()
    return row

