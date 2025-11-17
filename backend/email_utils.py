import os
import requests


# ----------------------------------------------------
# ENV CONFIG
# ----------------------------------------------------
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # Example: "playground@yourdomain.com"


def send_email(to: str, subject: str, html: str):
    """
    Sends a single HTML email via Resend API.
    Returns response object if successful, None otherwise.
    """
    if not RESEND_API_KEY:
        print("❌ Missing RESEND_API_KEY. Check Render environment variables.")
        return None
    
    if not FROM_EMAIL:
        print("❌ Missing FROM_EMAIL. Check Render environment variables.")
        return None

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "from": FROM_EMAIL,
        "to": to,
        "subject": subject,
        "html": html,
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print("📬 Resend Response:", response.status_code, response.text)
        if response.status_code == 200:
            return response
        else:
            print(f"❌ Resend API returned error: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print("❌ Error sending email: Request timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending email: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error sending email: {e}")
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


def send_match_email_to_founder(founder, designer):
    """
    Sends a match notification email to the founder.
    """
    subject = "Your Creative Partner Awaits 🎉"
    founder_name = founder.get("full_name")
    designer_name = designer.get("full_name")
    designer_email = designer.get("email")
    
    html = f"""
    <p>Hi {founder_name},</p>
    <p>You've been matched with a designer!</p>
    <p>Here are their details:</p>
    <p><strong>Name:</strong> {designer_name}</p>
    <p><strong>Email:</strong> {designer_email}</p>
    <p>You can reach out and start the conversation whenever you like.</p>
    <p>If this match isn't the right fit, let us know and we'll get you rematched with someone new. We've got you!</p>
    <br>
    <p>– The Playground Team</p>
    """
    
    send_email(
        to=founder.get("email"),
        subject=subject,
        html=html
    )


def send_match_email_to_designer(designer, founder):
    """
    Sends a match notification email to the designer.
    """
    subject = "You've Been Matched! 🎨✨"
    designer_name = designer.get("full_name")
    founder_name = founder.get("full_name")
    founder_email = founder.get("email")
    
    html = f"""
    <p>Hi {designer_name},</p>
    <p>Great news — you've been matched with a founder!</p>
    <p>Here are their details:</p>
    <p><strong>Name:</strong> {founder_name}</p>
    <p><strong>Email:</strong> {founder_email}</p>
    <p>Feel free to reach out and introduce yourself whenever you're ready.</p>
    <p>If the match doesn't feel right for any reason, you can request a rematch anytime. No pressure — the goal is to help you find a great collaboration.</p>
    <p>You'll hear from us again soon!</p>
    <br>
    <p>– The Playground Team</p>
    """
    
    send_email(
        to=designer.get("email"),
        subject=subject,
        html=html
    )


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
