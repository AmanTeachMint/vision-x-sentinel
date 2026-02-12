"""Email content generator for intervention alerts."""
from datetime import datetime

from app.config import Config


class EmailGenerator:
    """Generate dynamic email content for intervention alerts."""

    def generate_email_content(self, classroom_name, chi_score, primary_issue, duration_mins):
        # Links (placeholders or configured)
        snapshot_url = getattr(Config, "SNAPSHOT_PLACEHOLDER_URL", "#")
        live_feed_url = getattr(Config, "DASHBOARD_URL", "#")

        if chi_score < 50:
            subject = (
                f"⚠️ Intervention Required: {classroom_name} Health Score Critical ({chi_score}/100)"
            )
        elif chi_score < 70:
            subject = (
                f"⚠️ Warning: {classroom_name} Behavioral Stability Dropping ({chi_score}/100)"
            )
        else:
            subject = f"📊 Daily Summary: {classroom_name}"

        if primary_issue == "missing_teacher":
            recommendation = "UNSUPERVISED SESSION - Deploy Hallway Monitor."
        elif primary_issue == "mischief":
            recommendation = "BEHAVIORAL RISK - Deploy Security."
        elif primary_issue == "loud_noise":
            recommendation = "DISTRACTION ALERT - Notify teacher via intercom."
        else:
            recommendation = "RISK ALERT - Review classroom conditions."

        if primary_issue == "missing_teacher":
            alert_type = "Missing Teacher"
        elif primary_issue == "mischief":
            alert_type = "Mischief"
        elif primary_issue == "loud_noise":
            alert_type = "Loud Noise"
        else:
            alert_type = primary_issue

        year = datetime.now().year

        body = (
            f"<div style=\"max-width:640px;margin:0 auto;border:1px solid #dbeafe;"
            f"border-radius:18px;overflow:hidden;font-family:Arial,sans-serif;\">"
            f"<div style=\"background:#2590f4;color:#fff;text-align:center;padding:28px 16px;\">"
            f"<div style=\"font-size:28px;font-weight:700;letter-spacing:1px;\">SYSTEM NOTIFICATION</div>"
            f"<div style=\"font-size:18px;margin-top:6px;\">Activity Detected: {{alert_type}}</div>"
            f"</div>"
            f"<div style=\"padding:24px 28px;background:#fff;color:#3f3f46;\">"
            f"<p style=\"font-size:20px;margin:0 0 10px 0;\">Hello Admin,</p>"
            f"<p style=\"font-size:16px;margin:0 0 18px 0;\">"
            f"The classroom monitoring system has found an activity in your class "
            f"that requires your attention.</p>"
            f"<div style=\"background:#e8f2ff;border-radius:14px;padding:18px 20px;\">"
            f"<p style=\"margin:0 0 10px 0;font-size:18px;color:#1d4ed8;\">"
            f"<b>Classroom :</b> {classroom_name}</p>"
            f"<p style=\"margin:0 0 10px 0;font-size:18px;color:#1d4ed8;\">"
            f"<b>Activity :</b> {alert_type}</p>"
            f"<p style=\"margin:0;font-size:18px;color:#1d4ed8;\">"
            f"<b>Duration :</b> {duration_mins} min</p>"
            f"</div>"
            f"<div style=\"margin:24px 0;display:flex;gap:16px;justify-content:center;\">"
            f"<a href=\"{snapshot_url}\" "
            f"style=\"background:#2590f4;color:#fff;text-decoration:none;"
            f"padding:12px 18px;border-radius:999px;font-weight:600;\">View Snapshot</a>"
            f"<a href=\"{live_feed_url}\" "
            f"style=\"background:#2590f4;color:#fff;text-decoration:none;"
            f"padding:12px 18px;border-radius:999px;font-weight:600;\">View Live Feed</a>"
            f"</div>"
            f"<p style=\"margin:0 0 8px 0;font-size:14px;color:#6b7280;\">"
            f"<b>Risk Analysis:</b> CHI {chi_score}/100, Primary Factor: {alert_type}</p>"
            f"<p style=\"margin:0 0 8px 0;font-size:14px;color:#6b7280;\">"
            f"<b>Recommendation:</b> {recommendation}</p>"
            f"</div>"
            f"<div style=\"padding:14px 20px;background:#f8fafc;text-align:center;"
            f"color:#94a3b8;font-size:12px;border-top:1px solid #e2e8f0;\">"
            f"This is an automated report from your Smart Panel Camera System.<br/>"
            f"© {year} Monitoring Department"
            f"</div>"
            f"</div>"
        )

        return {"subject": subject, "body": body}

    def generate_intervention_email(self, classroom_name, chi_score, primary_issue, to_email="admin@school.org"):
        content = self.generate_email_content(
            classroom_name=classroom_name,
            chi_score=chi_score,
            primary_issue=primary_issue,
            duration_mins=5,
        )

        return {
            "to": to_email,
            "from": "sentinel-ai@school.org",
            "subject": content["subject"],
            "body": content["body"],
        }
