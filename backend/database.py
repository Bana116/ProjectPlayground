import os
import sqlite3
from pathlib import Path

# Detect database type from environment
DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = Path(__file__).resolve().parent / "matcher.db"

# Determine if we're using PostgreSQL or SQLite
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgres")

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor


# -----------------------------
# DATABASE CONNECTION HELPERS
# -----------------------------
def get_connection():
    """Get database connection (PostgreSQL or SQLite)"""
    if USE_POSTGRES:
        # Parse DATABASE_URL (format: postgres://user:pass@host:port/dbname)
        # Render sometimes provides postgres://, sometimes postgresql://
        db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(db_url)
    else:
        return sqlite3.connect(DB_PATH)


def get_cursor(conn):
    """Get database cursor with appropriate settings"""
    if USE_POSTGRES:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        return conn.cursor()


def get_placeholder():
    """Get the correct placeholder for parameterized queries"""
    return "%s" if USE_POSTGRES else "?"


# -----------------------------
# INIT: Create tables if missing
# -----------------------------
def init_db():
    conn = get_connection()
    cur = get_cursor(conn)

    # Designers table
    if USE_POSTGRES:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS designers (
            id SERIAL PRIMARY KEY,
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
    else:
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
    if USE_POSTGRES:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS founders (
            id SERIAL PRIMARY KEY,
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
    else:
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

    # Matches table (for database_matches.py)
    if USE_POSTGRES:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            founder_email TEXT,
            designer_email TEXT,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            founder_email TEXT,
            designer_email TEXT,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.commit()
    conn.close()


# -----------------------------
# SAVE DESIGNER
# -----------------------------
def save_designer(data):
    conn = None
    try:
        conn = get_connection()
        cur = get_cursor(conn)
        placeholder = get_placeholder()

        # Ensure all list fields are lists
        availability = data.get("availability", []) or []
        focus = data.get("focus", []) or []
        interest_areas = data.get("interest_areas", []) or []
        unpaid_experience = data.get("unpaid_experience", []) or []
        goals = data.get("goals", []) or []
        niche_interest = data.get("niche_interest", []) or []
        tools = data.get("tools", []) or []
        figma_experience = data.get("figma_experience", []) or []
        resources = data.get("resources", []) or []

        cur.execute(f"""
            INSERT INTO designers (
                full_name, email, city_country, portfolio,
                availability, focus, interest_areas,
                unpaid_experience, goals, niche_interest,
                tools, figma_experience, resources,
                extra_notes, newsletter
            )
            VALUES ({', '.join([placeholder] * 15)})
        """, (
            data.get("full_name", ""),
            data.get("email", ""),
            data.get("city_country", "") or "",
            data.get("portfolio", "") or "",
            ",".join(availability) if availability else "",
            ",".join(focus) if focus else "",
            ",".join(interest_areas) if interest_areas else "",
            ",".join(unpaid_experience) if unpaid_experience else "",
            ",".join(goals) if goals else "",
            ",".join(niche_interest) if niche_interest else "",
            ",".join(tools) if tools else "",
            ",".join(figma_experience) if figma_experience else "",
            ",".join(resources) if resources else "",
            data.get("extra_notes", "") or "",
            data.get("newsletter", "") or ""
        ))

        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error in save_designer: {e}")
        raise  # Re-raise so caller can handle it
    finally:
        if conn:
            conn.close()


# -----------------------------
# SAVE FOUNDER
# -----------------------------
def save_founder(data):
    conn = None
    try:
        conn = get_connection()
        cur = get_cursor(conn)
        placeholder = get_placeholder()

        # Ensure all list fields are lists
        project_stage = data.get("project_stage", []) or []
        design_help = data.get("design_help", []) or []
        paid_role = data.get("paid_role", []) or []
        niche = data.get("niche", []) or []
        support_level = data.get("support_level", []) or []

        cur.execute(f"""
            INSERT INTO founders (
                full_name, email, project_name, website,
                project_stage, design_help, tools_used,
                paid_role, niche, estimated_hours,
                beginner_friendly, support_level, extra_notes
            )
            VALUES ({', '.join([placeholder] * 13)})
        """, (
            data.get("full_name", ""),
            data.get("email", ""),
            data.get("project_name", ""),
            data.get("website", ""),
            ",".join(project_stage) if project_stage else "",
            ",".join(design_help) if design_help else "",
            data.get("tools_used", "") or "",
            ",".join(paid_role) if paid_role else "",
            ",".join(niche) if niche else "",
            data.get("estimated_hours", "") or "",
            data.get("beginner_friendly", "") or "",
            ",".join(support_level) if support_level else "",
            data.get("extra_notes", "") or ""
        ))

        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error in save_founder: {e}")
        raise  # Re-raise so caller can handle it
    finally:
        if conn:
            conn.close()


# -----------------------------
# FETCH ALL
# -----------------------------
def get_all_designers():
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("SELECT * FROM designers")
    
    if USE_POSTGRES:
        rows = cur.fetchall()
        # Convert RealDictRow to tuple for compatibility
        rows = [tuple(row.values()) for row in rows]
    else:
        rows = cur.fetchall()
    
    conn.close()
    return rows


def get_all_founders():
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("SELECT * FROM founders")
    
    if USE_POSTGRES:
        rows = cur.fetchall()
        # Convert RealDictRow to tuple for compatibility
        rows = [tuple(row.values()) for row in rows]
    else:
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
    conn = get_connection()
    cur = get_cursor(conn)
    placeholder = get_placeholder()
    cur.execute(f"SELECT * FROM founders WHERE id = {placeholder}", (founder_id,))
    
    if USE_POSTGRES:
        row = cur.fetchone()
        if row:
            row = tuple(row.values())
    else:
        row = cur.fetchone()
    
    conn.close()
    return row
