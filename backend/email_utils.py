import os
import requests


# ----------------------------------------------------
# ENV CONFIG
# ----------------------------------------------------
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # Example: "playground@yourdomain.com"


def send_email(to_email: str, subject: str, message: str):
    """
    Sends a single HTML email via Resend API.
    """
    if not RESEND_API_KEY:
        print("❌ Missing RESEND_API_KEY. Check Render environment variables.")
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

    try:
        response = requests.post(url, json=data, headers=headers)
        print("📬 Resend Response:", response.status_code, response.text)
        return response
    except Exception as e:
        print("❌ Error sending email:", e)
        return None


# ----------------------------------------------------
# HELPERS FOR MATCHING EMAILS
# ----------------------------------------------------

def _format_niche(niche_value):
    """
    Ensure niche prints cleanly even if it's a list or empty.
    """
    if isinstance(niche_value, list):
        return ", ".join(niche_value) if niche_value else "Not provided"
    return niche_value or "Not provided"


def send_founder_match_email(founder: dict, designer: dict, score: float) -> None:
    """
    Sends an email to the founder with their top designer match.
    """
    subject = "Your designer match is ready 🎯"
    niche_display = _format_niche(founder.get("niche"))

    html = f"""
    <p>Hey {founder.get("full_name")},</p>
    <p>We found a designer who looks like a strong match for your project.</p>

    <h3>Designer Match</h3>
    <ul>
        <li><strong>Name:</strong> {designer.get("full_name")}</li>
        <li><strong>Email:</strong> {designer.get("email")}</li>
        <li><strong>Location:</strong> {designer.get("city_country") or "Not provided"}</li>
        <li><strong>Portfolio:</strong> {designer.get("portfolio") or "Not provided"}</li>
        <li><strong>Match Score:</strong> {int(score * 100)}%</li>
    </ul>

    <h3>Your Project</h3>
    <ul>
        <li><strong>Project Name:</strong> {founder.get("project_name") or "Not provided"}</li>
        <li><strong>Niche:</strong> {niche_display}</li>
        <li><strong>Beginner Friendly:</strong> {founder.get("beginner_friendly") or "Not specified"}</li>
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
    Sends an email to the designer that they’ve been matched with a project.
    """
    subject = "You’ve been matched with a new project ✨"
    niche_display = _format_niche(founder.get("niche"))

    html = f"""
    <p>Hey {designer.get("full_name")},</p>
    <p>You’ve been matched with a project that aligns with your skills and interests.</p>

    <h3>Project Details</h3>
    <ul>
        <li><strong>Founder:</strong> {founder.get("full_name")}</li>
        <li><strong>Email:</strong> {founder.get("email")}</li>
        <li><strong>Project Name:</strong> {founder.get("project_name") or "Not provided"}</li>
        <li><strong>Niche:</strong> {niche_display}</li>
        <li><strong>Match Score:</strong> {int(score * 100)}%</li>
    </ul>

    <p>If it feels interesting, send them a short intro and see if it’s a good fit.</p>
    <p style="opacity:0.7;">– Playground</p>
    """

    send_email(
        to_email=designer.get("email"),
        subject=subject,
        message=html,
    )
