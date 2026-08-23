import logging
import httpx
from app.core.config import settings

logger = logging.getLogger("nexus.email")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[EMAIL NOTIFICATION] %(asctime)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends email via Resend API if RESEND_API_KEY is configured.
    Otherwise falls back to structured console logging.
    """
    if settings.RESEND_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": "NEXUS Society <notifications@nexus.society>",
                        "to": [to_email],
                        "subject": subject,
                        "html": f"<div style='font-family:sans-serif; padding:20px;'><h2>{subject}</h2><p>{body}</p></div>"
                    },
                    timeout=5.0
                )
                if res.status_code in (200, 201):
                    logger.info(f"Resend API successfully sent email to {to_email}: {subject}")
                    return True
                else:
                    logger.warning(f"Resend API status {res.status_code}: {res.text}. Falling back to console log.")
        except Exception as e:
            logger.error(f"Error calling Resend API: {e}. Falling back to console log.")

    # Fallback console dispatch
    logger.info(f"DISPATCHED to [{to_email}] | Subject: '{subject}' | Body: '{body[:100]}...'")
    return True

async def notify_complaint_status_change(user_email: str, complaint_id: str, old_status: str, new_status: str, note: str = ""):
    subject = f"Complaint INC-{complaint_id[:8].upper()} Status Updated to '{new_status}'"
    body = f"Your complaint INC-{complaint_id[:8].upper()} has transitioned from '{old_status}' to '{new_status}'."
    if note:
        body += f"\nNote from admin: {note}"
    await send_email(user_email, subject, body)

async def notify_important_notice(user_emails: list[str], notice_title: str, notice_body: str):
    subject = f"IMPORTANT SOCIETY NOTICE: {notice_title}"
    body = f"An important notice has been posted by the administration:\n\n{notice_body}"
    for email in user_emails:
        await send_email(email, subject, body)
