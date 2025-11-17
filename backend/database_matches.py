# database_matches.py
from .database import get_connection, get_cursor, get_placeholder, USE_POSTGRES


# --------------------------
# Save a new match to log
# --------------------------
def save_match_record(founder_email: str, designer_email: str, score: float):
    conn = get_connection()
    cur = get_cursor(conn)
    placeholder = get_placeholder()
    
    cur.execute(f"""
        INSERT INTO matches (founder_email, designer_email, score)
        VALUES ({placeholder}, {placeholder}, {placeholder})
    """, (founder_email, designer_email, score))
    
    conn.commit()
    conn.close()


# --------------------------
# Read all match logs
# --------------------------
def get_all_match_records():
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("SELECT * FROM matches ORDER BY created_at DESC")
    
    if USE_POSTGRES:
        rows = cur.fetchall()
        # Convert to list of dicts
        records = [
            {
                "founder": row["founder_email"],
                "designer": row["designer_email"],
                "score": float(row["score"]),
                "id": row["id"],
                "created_at": str(row["created_at"]) if row.get("created_at") else None
            }
            for row in rows
        ]
    else:
        rows = cur.fetchall()
        # Convert tuples to dicts
        records = [
            {
                "founder": row[1],
                "designer": row[2],
                "score": float(row[3]),
                "id": row[0],
                "created_at": str(row[4]) if len(row) > 4 and row[4] else None
            }
            for row in rows
        ]
    
    conn.close()
    return records
