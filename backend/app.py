from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from . import database
from .email_utils import send_email


# ------------------------------
# BASE DIR
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

database.init_db()

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
    try:
        data = {
            "full_name": full_name,
            "email": email,
            "city_country": city_country or "",
            "portfolio": portfolio or "",
            "availability": availability if availability else [],
            "focus": focus if focus else [],
            "interest_areas": interest_areas if interest_areas else [],
            "unpaid_experience": unpaid_experience if unpaid_experience else [],
            "goals": goals if goals else [],
            "niche_interest": niche_interest if niche_interest else [],
            "tools": tools if tools else [],
            "figma_experience": figma_experience if figma_experience else [],
            "resources": resources if resources else [],
            "extra_notes": extra_notes or "",
            "newsletter": newsletter or "",
        }

        # Save designer to database
        try:
            database.save_designer(data)
        except Exception as e:
            print(f"❌ Error saving designer to database: {e}")
            # Still continue - don't fail the whole request
            # In production, you might want to log this and alert

        # Send designer confirmation email (non-blocking - don't fail if email fails)
        try:
            send_email(
                to=email,
                subject="You're in the designer playground 🎠",
                html=f"""
                    <h2>Welcome to Playground, {full_name}!</h2>
                    <p>You're officially in. We'll match you with founders and projects that fit your skills and curiosity.</p>
                    <p>You can update your info anytime by submitting the form again using the same email.</p>
                    <br>
                    <p style="opacity:0.6;font-size:14px;">— The Playground Engine</p>
                """
            )
        except Exception as e:
            print(f"❌ Error sending confirmation email: {e}")
            # Continue - email failure shouldn't break the form submission

        return templates.TemplateResponse(
            "designer_submitted.html",
            {"request": request, "data": data}
        )
    
    except Exception as e:
        print(f"❌ Critical error in submit_designer: {e}")
        import traceback
        traceback.print_exc()
        # Return error page instead of 500
        return templates.TemplateResponse(
            "designer_submitted.html",
            {"request": request, "data": {"error": "There was an error processing your submission. Please try again."}},
            status_code=200  # Still return 200 to show the page, but with error message
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
    try:
        founder = {
            "full_name": full_name,
            "email": email,
            "project_name": project_name,
            "website": website,
            "project_stage": project_stage if project_stage else [],
            "design_help": design_help if design_help else [],
            "tools_used": tools_used or "",
            "paid_role": paid_role if paid_role else [],
            "niche": niche if niche else [],
            "estimated_hours": estimated_hours or "",
            "beginner_friendly": beginner_friendly or "",
            "support_level": support_level if support_level else [],
            "extra_notes": extra_notes or "",
        }

        # Save founder to database
        try:
            database.save_founder(founder)
        except Exception as e:
            print(f"❌ Error saving founder to database: {e}")
            # Still continue - don't fail the whole request
            # In production, you might want to log this and alert

        # Send founder confirmation email (non-blocking - don't fail if email fails)
        try:
            send_email(
                to=email,
                subject="You're in! 🎉",
                html=f"""
                    <h2>Welcome to Playground, {full_name}!</h2>
                    <p>Thanks for submitting <strong>{project_name or "your project"}</strong>.</p>
                    <p>We've received your submission and will be in touch soon.</p>
                    <br>
                    <p style="opacity:0.6;font-size:14px;">— The Playground Engine</p>
                """
            )
        except Exception as e:
            print(f"❌ Error sending confirmation email: {e}")
            # Continue - email failure shouldn't break the form submission

        return templates.TemplateResponse(
            "founder_submitted.html",
            {"request": request, "data": founder}
        )
    
    except Exception as e:
        print(f"❌ Critical error in submit_founder: {e}")
        import traceback
        traceback.print_exc()
        # Return error page instead of 500
        return templates.TemplateResponse(
            "founder_submitted.html",
            {"request": request, "data": {"error": "There was an error processing your submission. Please try again."}},
            status_code=200  # Still return 200 to show the page, but with error message
        )


# ------------------------------
# ADMIN — view match logs
# ------------------------------
@app.get("/admin/matches")
def view_matches():
    try:
        from .database_matches import get_all_match_records
        records = get_all_match_records()
        return records
    except Exception as e:
        print(f"❌ Error in view_matches: {e}")
        import traceback
        traceback.print_exc()
        return {"error": "Failed to retrieve matches"}


# ------------------------------
# ADMIN DEBUG ENDPOINTS (for Render)
# ------------------------------

@app.get("/admin/designers")
def admin_designers():
    try:
        from .database import get_all_designers
        designers = get_all_designers()
        return designers
    except Exception as e:
        print(f"❌ Error in admin_designers: {e}")
        import traceback
        traceback.print_exc()
        return {"error": "Failed to retrieve designers"}


@app.get("/admin/founders")
def admin_founders():
    try:
        from .database import get_all_founders
        founders = get_all_founders()
        return founders
    except Exception as e:
        print(f"❌ Error in admin_founders: {e}")
        import traceback
        traceback.print_exc()
        return {"error": "Failed to retrieve founders"}

@app.get("/admin/raw-matches")
def admin_raw_matches():
    try:
        from .database_matches import get_all_match_records
        records = get_all_match_records()
        return records
    except Exception as e:
        print(f"❌ Error in admin_raw_matches: {e}")
        import traceback
        traceback.print_exc()
        return {"error": "Failed to retrieve match records"}
