# email_utils.py
import os
import requests

# -----------------------------
# Base config (from .env)
# -----------------------------
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # e.g. "bana.asmaa@gmail.com"


def send_email(to_email: str, subject: str, message: str):
    """
    Low-level helper that sends a single HTML email via Resend.
    """
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY is missing. Check your .env.")
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "from": FROM_EMAIL,
        "to": to_email,
        "subject": subject,
        "html": message,
    }

    response = requests.post(url, json=data, headers=headers)
    print("📬 Resend response:", response.status_code, response.text)
    return response


# -----------------------------
# Matching email helpers
# -----------------------------

def _format_niche(niche_value):
    """Handle niche as list or string nicely."""
    if isinstance(niche_value, list):
        return ", ".join(niche_value) if niche_value else "Not provided"
    return niche_value or "Not provided"


def send_founder_match_email(founder: dict, designer: dict, score: float) -> None:
    """
    Email the founder their top designer match.
    """
    subject = "Your designer match is ready 🎯"

    niche_display = _format_niche(founder.get("niche"))

    html = f"""
    <p>Hey {founder.get("full_name")},</p>
    <p>We found a designer who looks like a strong match for your project.</p>

    <h3>Designer match</h3>
    <ul>
        <li><strong>Name:</strong> {designer.get("full_name")}</li>
        <li><strong>Email:</strong> {designer.get("email")}</li>
        <li><strong>Location:</strong> {designer.get("city_country") or "Not provided"}</li>
        <li><strong>Portfolio:</strong> {designer.get("portfolio") or "Not provided"}</li>
        <li><strong>Match score:</strong> {int(score * 100)}%</li>
    </ul>

    <h3>Your project</h3>
    <ul>
        <li><strong>Project name:</strong> {founder.get("project_name") or "Not provided"}</li>
        <li><strong>Niche:</strong> {niche_display}</li>
        <li><strong>Beginner-friendly:</strong> {founder.get("beginner_friendly") or "Not specified"}</li>
    </ul>

    <p>Feel free to reach out directly and see if the vibe fits ✨</p>
    <p style="opacity:0.7;">– Playground</p>
    """

    send_email(
        to_email=founder.get("email"),
        subject=subject,
        message=html,
    )


def send_designer_match_email(designer: dict, founder: dict, score: float) -> None:
    """
    Email the designer that they've been matched with a project.
    """
    subject = "You’ve been matched with a new project ✨"

    niche_display = _format_niche(founder.get("niche"))

    html = f"""
    <p>Hey {designer.get("full_name")},</p>
    <p>You’ve been matched with a project that looks aligned with your skills and interests.</p>

    <h3>Founder & project</h3>
    <ul>
        <li><strong>Founder:</strong> {founder.get("full_name")}</li>
        <li><strong>Email:</strong> {founder.get("email")}</li>
        <li><strong>Project name:</strong> {founder.get("project_name") or "Not provided"}</li>
        <li><strong>Niche:</strong> {niche_display}</li>
        <li><strong>Match score:</strong> {int(score * 100)}%</li>
    </ul>

    <p>If it feels interesting, send them a short intro and see if it’s a good fit.</p>
    <p style="opacity:0.7;">– Playground</p>
    """

    send_email(
        to_email=designer.get("email"),
        subject=subject,
        message=html,
    )
