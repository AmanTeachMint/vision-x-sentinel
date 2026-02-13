"""Alerts API: GET list, trigger-email (test), optionally filtered by classroom_id."""
from flask import Blueprint, request, jsonify

from app.db.store import get_alerts, get_classroom_by_id
from app.sentinel.email_service import EmailGenerator, send_email_to_admin

bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def list_alerts():
    """GET /api/alerts — return all alerts, optionally filtered by classroom_id."""
    classroom_id = request.args.get('classroom_id')
    limit = request.args.get('limit', type=int)
    alerts = get_alerts(classroom_id=classroom_id, limit=limit)
    return jsonify(alerts)


@bp.route('/trigger-email', methods=['POST'])
def trigger_email():
    """
    POST /api/alerts/trigger-email
    Body: { "classroom_id": "8A", "score": 45, "issue": "mischief", "snapshot_url": "/api/snapshots/8A_mischief_xxx.jpg" }
    Returns generated email JSON. If SMTP and ADMIN_EMAIL are set, also sends the email to admin.
    """
    data = request.get_json(silent=True) or {}
    classroom_id = data.get("classroom_id")
    score = data.get("score", 0)
    issue = data.get("issue")
    snapshot_url = data.get("snapshot_url")

    if not classroom_id or not issue:
        return jsonify({"error": "classroom_id and issue are required"}), 400

    classroom = get_classroom_by_id(classroom_id) or {}
    classroom_name = classroom.get("name") or classroom_id

    generator = EmailGenerator()
    email = generator.generate_intervention_email(classroom_name, score, issue, snapshot_url)

    # Optionally send to admin if configured
    sent = send_email_to_admin(classroom_name, score, issue, snapshot_url=snapshot_url)
    email["sent_to_admin"] = sent

    return jsonify(email)
