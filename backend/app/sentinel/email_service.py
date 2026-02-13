"""Email service: generate intervention email content and send to admin via SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import Config


class EmailGenerator:
    """Generate intervention email content (subject, body) for alerts."""

    @staticmethod
    def generate_intervention_email(
        classroom_name: str,
        score: float,
        issue: str,
        snapshot_url: str = None,
    ) -> dict:
        """
        Build email payload for an alert.
        :param classroom_name: e.g. "Class 8A"
        :param score: severity/score (e.g. motion_score, audio_level, or 0 for empty_class)
        :param issue: one of "empty_class", "mischief", "loud_noise"
        :param snapshot_url: optional URL to snapshot image (e.g. /api/snapshots/8A_mischief_xxx.jpg)
        :return: dict with subject, body_plain, body_html (and snapshot_url if provided)
        """
        issue_labels = {
            "empty_class": "Empty classroom",
            "mischief": "Mischief / high motion",
            "loud_noise": "Loud noise",
        }
        label = issue_labels.get(issue, issue)

        subject = f"[VisionX Sentinel] {label} – {classroom_name}"
        body_plain = (
            f"VisionX Sentinel Alert\n"
            f"Classroom: {classroom_name}\n"
            f"Issue: {label}\n"
            f"Score: {score}\n\n"
        )
        if snapshot_url:
            body_plain += f"Snapshot: {snapshot_url}\n"
        body_plain += "\nPlease check the classroom or dashboard for details."

        body_html = (
            f"<p><strong>VisionX Sentinel Alert</strong></p>"
            f"<p>Classroom: <strong>{classroom_name}</strong></p>"
            f"<p>Issue: {label}</p>"
            f"<p>Score: {score}</p>"
        )
        if snapshot_url:
            body_html += f'<p><a href="{snapshot_url}">View snapshot</a></p>'
        body_html += "<p>Please check the classroom or dashboard for details.</p>"

        out = {
            "subject": subject,
            "body_plain": body_plain,
            "body_html": body_html,
        }
        if snapshot_url:
            out["snapshot_url"] = snapshot_url
        return out


def send_email_to_admin(
    classroom_name: str,
    score: float,
    issue: str,
    snapshot_url: str = None,
    base_url: str = None,
) -> bool:
    """
    Send intervention email to ADMIN_EMAIL via SMTP.
    If SMTP or ADMIN_EMAIL is not configured, logs and returns False.
    :param base_url: optional base URL (e.g. https://api.example.com) to turn snapshot path into full URL
    """
    if not Config.ADMIN_EMAIL or not Config.SMTP_HOST or not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD:
        print("[email_service] Skipping email: SMTP not configured (set ADMIN_EMAIL, SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD in .env)")
        return False

    # Gmail app passwords are 16 chars; .env sometimes has spaces for readability – strip them
    smtp_password = (Config.SMTP_PASSWORD or "").replace(" ", "").strip()
    if not smtp_password:
        print("[email_service] Skipping email: SMTP_PASSWORD is empty")
        return False

    # Make snapshot URL absolute for email link if base_url given
    final_snapshot_url = snapshot_url
    if base_url and snapshot_url and str(snapshot_url).startswith("/"):
        final_snapshot_url = base_url.rstrip("/") + snapshot_url

    payload = EmailGenerator.generate_intervention_email(
        classroom_name, score, issue, final_snapshot_url
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = payload["subject"]
    msg["From"] = Config.SMTP_FROM
    msg["To"] = Config.ADMIN_EMAIL
    msg.attach(MIMEText(payload["body_plain"], "plain"))
    msg.attach(MIMEText(payload["body_html"], "html"))

    try:
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(Config.SMTP_USERNAME, smtp_password)
            server.sendmail(Config.SMTP_FROM, [Config.ADMIN_EMAIL], msg.as_string())
        print(f"[email_service] Alert email sent to {Config.ADMIN_EMAIL}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[email_service] SMTP login failed (check username/app password): {e}")
        return False
    except Exception as e:
        print(f"[email_service] Failed to send alert email to admin: {e}")
        return False
