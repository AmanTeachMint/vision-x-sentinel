"""Email content generator for intervention alerts."""


class EmailGenerator:
    """Generate dynamic email content for intervention alerts."""

    def generate_email_content(self, classroom_name, chi_score, primary_issue, duration_mins):
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

        body = (
            f"<p><b>Automated Supervision Report</b></p>"
            f"<p><b>Risk Analysis</b></p>"
            f"<p>Current CHI Score: <b>{chi_score}/100</b></p>"
            f"<p>Primary Factor: <b>{primary_issue}</b></p>"
            f"<p><b>Recommendation</b></p>"
            f"<p>{recommendation}</p>"
            f"<p>Duration: <b>{duration_mins} min</b></p>"
            f"<p>[ 📸 View Snapshot ] [ 🔴 Watch Live Feed ]</p>"
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
