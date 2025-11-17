from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from email_utils import send_designer_confirmation, send_founder_confirmation

# ------------------------------
# App Setup
# ------------------------------

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="frontend")

DATABASE = "matcher.db"


# ------------------------------
# Database Helpers
# ------------------------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Designer Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS designers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            availability TEXT,
            experience_interests TEXT,
            niche_interests TEXT,
            tools_comfort TEXT,
            figma_skill TEXT
        )
    """)

    # Founder Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS founders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            design_help_needed TEXT,
            project_niche TEXT,
            weekly_hours TEXT,
            founder_support TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ------------------------------
# ROUTES — Page Views
# ------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/designer", response_class=HTMLResponse)
def designer_form(request: Request):
    return templates.TemplateResponse("designer.html", {"request": request})


@app.get("/founder", response_class=HTMLResponse)
def founder_form(request: Request):
    return templates.TemplateResponse("founder.html", {"request": request})


# ------------------------------
# ROUTES — Form Submissions
# ------------------------------

@app.post("/submit-designer")
async def submit_designer(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    availability: str = Form(...),
    experience_interests: list[str] = Form(None),
    niche_interests: list[str] = Form(None),
    tools_comfort: list[str] = Form(None),
    figma_skill: str = Form(...)
):
    # Convert lists → comma-separated strings
    experience_str = ", ".join(experience_interests or [])
    niche_str = ", ".join(niche_interests or [])
    tools_str = ", ".join(tools_comfort or [])

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO designers (name, email, availability, experience_interests,
                               niche_interests, tools_comfort, figma_skill)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, availability, experience_str, niche_str, tools_str, figma_skill))
    conn.commit()
    conn.close()

    # send confirmation email
    try:
        send_designer_confirmation(name=name, email=email)
    except Exception as e:
        print("Email error:", e)

    return templates.TemplateResponse(
        "confirmation.html",
        {"request": request, "role": "designer"}
    )


@app.post("/submit-founder")
async def submit_founder(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    design_help_needed: list[str] = Form(None),
    project_niche: list[str] = Form(None),
    weekly_hours: str = Form(...),
    founder_support: str = Form(...)
):
    # Convert multi-select lists → strings
    help_str = ", ".join(design_help_needed or [])
    niche_str = ", ".join(project_niche or [])

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO founders (name, email, design_help_needed,
                              project_niche, weekly_hours, founder_support)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, help_str, niche_str, weekly_hours, founder_support))
    conn.commit()
    conn.close()

    # Send founder confirmation email
    try:
        send_founder_confirmation(name=name, email=email)
    except Exception as e:
        print("Email error:", e)

    return templates.TemplateResponse(
        "confirmation.html",
        {"request": request, "role": "founder"}
    )


# ------------------------------
# Health Check (Render Needs This)
# ------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

