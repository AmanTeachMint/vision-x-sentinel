"""Alerts API: GET list, optionally filtered by classroom_id."""
from flask import Blueprint, request, jsonify

from app.db.store import get_alerts

bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def list_alerts():
    """GET /api/alerts — return all alerts, optionally filtered by classroom_id."""
    classroom_id = request.args.get('classroom_id')
    limit = request.args.get('limit', type=int)
    alerts = get_alerts(classroom_id=classroom_id, limit=limit)
    return jsonify(alerts)
