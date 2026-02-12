"""Alerts API: GET list, optionally filtered by classroom_id."""
from flask import Blueprint, request, jsonify

from app.db.store import get_alerts, get_classroom_by_id
from sentinel.email_service import EmailGenerator

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
    Body: { "classroom_id": "8A", "score": 45, "issue": "mischief" }
    Returns generated email JSON (mock).
    """
    data = request.get_json(silent=True) or {}
    classroom_id = data.get("classroom_id")
    score = data.get("score")
    issue = data.get("issue")

    if not classroom_id or score is None or not issue:
        return jsonify({"error": "classroom_id, score, and issue are required"}), 400

    classroom = get_classroom_by_id(classroom_id) or {}
    classroom_name = classroom.get("name") or classroom_id

    generator = EmailGenerator()
    email = generator.generate_intervention_email(classroom_name, score, issue)
    return jsonify(email)
