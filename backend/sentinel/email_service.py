"""Email content generator for intervention alerts."""


class EmailGenerator:
    """Generate dynamic email content for intervention alerts."""

    def generate_email_content(
        self,
        classroom_name,
        chi_score,
        primary_issue,
        duration_mins,
        incident_time=None,
        time_window=None,
        classroom_status=None,
        dashboard_url="#",
        snapshot_url=None,
    ):
        if chi_score < 50:
            subject = (
                f"⚠️ Intervention Required: {classroom_name} Health Score Critical ({chi_score}/100)"
            )
        elif chi_score < 70:
            subject = (
                f"⚠️ Warning: {classroom_name} Behavioral Stability Dropping ({chi_score}/100)"
            )
        else:
            subject = f"Status Update: {classroom_name} ({chi_score}/100)"

        if primary_issue == "missing_teacher":
            headline = "UNSUPERVISED SESSION"
            issue_label = "Missing Teacher"
            recommendation = "Deploy Hallway Monitor or Substitute immediately."
        elif primary_issue == "mischief":
            headline = "BEHAVIORAL RISK"
            issue_label = "Mischief"
            recommendation = "Deploy Security/Principal to room."
        elif primary_issue == "loud_noise":
            headline = "DISTRACTION ALERT"
            issue_label = "Loud Noise"
            recommendation = "Notify teacher via intercom to lower volume."
        else:
            headline = "RISK ALERT"
            issue_label = primary_issue
            recommendation = "Review classroom conditions."

        incident_time = incident_time or "Now"
        time_window = time_window or f"Last {duration_mins} min"
        classroom_status = classroom_status or primary_issue

        snapshot_block = ""
        if snapshot_url:
            snapshot_block = (
                f"<p><b>Snapshot</b></p>"
                f"<p><a href=\"{snapshot_url}\">View Snapshot</a></p>"
            )

        body = (
            f"<p><b>Risk Analysis</b></p>"
            f"<p><b>Headline:</b> {headline}</p>"
            f"<p><b>Classroom:</b> {classroom_name}</p>"
            f"<p><b>Incident Time:</b> {incident_time} "
            f"(<b>Window:</b> {time_window})</p>"
            f"<p><b>Data</b></p>"
            f"<ul>"
            f"<li><b>Classroom Status:</b> {classroom_status}</li>"
            f"<li><b>Score:</b> {chi_score}/100</li>"
            f"<li><b>Primary Factor:</b> {issue_label}</li>"
            f"<li><b>Duration:</b> {duration_mins} min</li>"
            f"</ul>"
            f"<p><b>Recommendation</b></p>"
            f"<p>{recommendation}</p>"
            f"{snapshot_block}"
            f"<p>"
            f"<a href=\"{dashboard_url}\" "
            f"style=\"display:inline-block;padding:10px 14px;"
            f"background:#2563eb;color:#fff;text-decoration:none;"
            f"border-radius:6px;\">View Live Feed</a>"
            f"</p>"
        )

        return {"subject": subject, "body": body}

    def generate_intervention_email(self, classroom_name, chi_score, primary_issue, to_email="admin@school.org"):
        content = self.generate_email_content(
            classroom_name=classroom_name,
            chi_score=chi_score,
            primary_issue=primary_issue,
            duration_mins=5,
            incident_time="Now",
            time_window="Last 5 min",
            classroom_status=primary_issue,
        )

        return {
            "to": to_email,
            "from": "sentinel-ai@school.org",
            "subject": content["subject"],
            "body": content["body"],
        }
