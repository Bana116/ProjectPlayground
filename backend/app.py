from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from . import database
from .match import match_score
from .emailer import send_email
from .email_utils import (
    send_founder_match_email,
    send_designer_match_email,
)
from .database_matches import save_match_record

# ------------------------------
# BASE DIR
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ------------------------------
# HOME
# ------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# ------------------------------
# DESIGNER FORM
# ------------------------------
@app.get("/designer", response_class=HTMLResponse)
def designer_page(request: Request):
    return templates.TemplateResponse("designer_form.html", {"request": request})


@app.post("/submit-designer", response_class=HTMLResponse)
async def submit_designer(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    city_country: str = Form(""),
    portfolio: str = Form(""),

    availability: list[str] = Form([]),
    focus: list[str] = Form([]),
    interest_areas: list[str] = Form([]),
    unpaid_experience: list[str] = Form([]),
    goals: list[str] = Form([]),
    niche_interest: list[str] = Form([]),
    tools: list[str] = Form([]),
    figma_experience: list[str] = Form([]),
    resources: list[str] = Form([]),

    extra_notes: str = Form(""),
    newsletter: str = Form("")
):
    data = {
        "full_name": full_name,
        "email": email,
        "city_country": city_country,
        "portfolio": portfolio,
        "availability": availability,
        "focus": focus,
        "interest_areas": interest_areas,
        "unpaid_experience": unpaid_experience,
        "goals": goals,
        "niche_interest": niche_interest,
        "tools": tools,
        "figma_experience": figma_experience,
        "resources": resources,
        "extra_notes": extra_notes,
        "newsletter": newsletter,
    }

    database.save_designer(data)

    # Designer welcome email
    send_email(
        to=email,
        subject="You're in the designer playground 🎠",
        html_content=f"""
            <h2>Welcome to Playground, {full_name}!</h2>
            <p>You’re officially in. We’ll match you with founders and projects that fit your skills and curiosity.</p>
            <p>You can update your info anytime by submitting the form again using the same email.</p>
            <br>
            <p style="opacity:0.6;font-size:14px;">— The Playground Engine</p>
        """
    )

    return templates.TemplateResponse(
        "designer_submitted.html",
        {"request": request, "data": data}
    )


# ------------------------------
# FOUNDER FORM
# ------------------------------
@app.get("/founder", response_class=HTMLResponse)
def founder_page(request: Request):
    return templates.TemplateResponse("founder_form.html", {"request": request})


@app.post("/submit-founder", response_class=HTMLResponse)
async def submit_founder(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    project_name: str = Form(""),
    website: str = Form(""),

    project_stage: list[str] = Form([]),
    design_help: list[str] = Form([]),
    tools_used: str = Form(""),
    paid_role: list[str] = Form([]),
    niche: list[str] = Form([]),
    estimated_hours: str = Form(""),
    beginner_friendly: str = Form(""),
    support_level: list[str] = Form([]),
    extra_notes: str = Form("")
):
    founder = {
        "full_name": full_name,
        "email": email,
        "project_name": project_name,
        "website": website,
        "project_stage": project_stage,
        "design_help": design_help,
        "tools_used": tools_used,
        "paid_role": paid_role,
        "niche": niche,
        "estimated_hours": estimated_hours,
        "beginner_friendly": beginner_friendly,
        "support_level": support_level,
        "extra_notes": extra_notes,
    }

    database.save_founder(founder)

    # Send founder: "welcome" email
    send_email(
        to=email,
        subject="You're in! 🎉",
        html_content=f"""
            <h2>Welcome to Playground, {full_name}!</h2>
            <p>Thanks for submitting <strong>{project_name or "your project"}</strong>.</p>
            <p>We’re now matching you with aligned designers.</p>
            <p>You’ll receive match emails shortly.</p>
            <br>
            <p style="opacity:0.6;font-size:14px;">— The Playground Engine</p>
        """
    )

    # --------------------------
    # AUTO-MATCHING
    # --------------------------
    designers = database.get_all_designers()
    formatted_designers = [database.format_designer(d) for d in designers]
    formatted_founder = database.format_founder(founder)

    ranked = []
    for d in formatted_designers:
        score = match_score(d, formatted_founder)
        ranked.append({"designer": d, "score": score})

    ranked.sort(key=lambda x: x["score"], reverse=True)

    if ranked:
        best = ranked[0]
        top_designer = best["designer"]
        top_score = best["score"]

        # Save match in database
        save_match_record(
            founder_email=email,
            designer_email=top_designer.get("email"),
            score=top_score
        )

        # Email both sides
        send_founder_match_email(formatted_founder, top_designer, top_score)
        send_designer_match_email(top_designer, formatted_founder, top_score)

    return templates.TemplateResponse(
        "founder_submitted.html",
        {"request": request, "data": founder}
    )


# ------------------------------
# ADMIN — view saved match logs
# ------------------------------
@app.get("/admin/matches")
def view_matches():
    from .database_matches import get_all_match_records
    return get_all_match_records()
