"""Admin profile API."""
from flask import Blueprint, jsonify

from app.db.store import get_admin_profile

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.route("/profile", methods=["GET"])
def get_profile():
    profile = get_admin_profile()
    if profile is None:
        return jsonify({"error": "Admin profile not found"}), 404
    return jsonify(profile)
