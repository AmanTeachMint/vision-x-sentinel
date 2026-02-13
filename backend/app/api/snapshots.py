"""Snapshots API: serve saved alert frames."""
import os
from flask import Blueprint, send_from_directory, jsonify

from app.config import Config

bp = Blueprint("snapshots", __name__, url_prefix="/api/snapshots")


@bp.route("/<path:filename>", methods=["GET"])
def get_snapshot(filename):
    """GET /api/snapshots/<filename> – serve a saved snapshot image."""
    snapshots_dir = Config.SNAPSHOTS_DIR
    path = os.path.join(snapshots_dir, filename)
    if not os.path.exists(path) or not os.path.isfile(path):
        return jsonify({"error": "Snapshot not found"}), 404
    return send_from_directory(snapshots_dir, filename)
