"""Snapshots API: serve saved frames."""
import os
from flask import Blueprint, send_from_directory, jsonify

from app.config import Config

bp = Blueprint("snapshots", __name__, url_prefix="/api/snapshots")


@bp.route("/<filename>", methods=["GET"])
def get_snapshot(filename):
    snapshots_dir = os.path.join(Config.BACKEND_ROOT, "static", "snapshots")
    path = os.path.join(snapshots_dir, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Snapshot not found"}), 404
    return send_from_directory(snapshots_dir, filename)
