"""Videos API: GET list, GET by id, POST to create/update."""
from flask import Blueprint, request, jsonify

from app.db.store import get_all_videos, get_video_by_id, upsert_video, delete_video

bp = Blueprint('videos', __name__, url_prefix='/api/videos')


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def list_videos():
    """GET /api/videos — return all videos, optionally filtered by classroom_id."""
    classroom_id = request.args.get('classroom_id')
    videos = get_all_videos(classroom_id=classroom_id)
    return jsonify(videos)


@bp.route('/<video_id>', methods=['GET'])
def get_video(video_id):
    """GET /api/videos/<id> — return one video or 404."""
    video = get_video_by_id(video_id)
    if video is None:
        return jsonify({'error': 'Video not found'}), 404
    return jsonify(video)


@bp.route('', methods=['POST'])
@bp.route('/', methods=['POST'])
def create_video():
    """POST /api/videos — create or update a video.
    Body: { "id": "video1", "filename": "video1.mp4", "url": "https://...", "classroom_id": "1" }
    """
    data = request.get_json(silent=True) or {}
    video_id = data.get('id')
    filename = data.get('filename')
    url = data.get('url')
    classroom_id = data.get('classroom_id')

    if not video_id:
        return jsonify({'error': 'id is required'}), 400
    if not filename:
        return jsonify({'error': 'filename is required'}), 400
    if not url:
        return jsonify({'error': 'url is required'}), 400

    video = upsert_video(video_id, filename, url, classroom_id)
    return jsonify(video), 201


@bp.route('/<video_id>', methods=['DELETE'])
def remove_video(video_id):
    """DELETE /api/videos/<id> — delete a video."""
    deleted = delete_video(video_id)
    if not deleted:
        return jsonify({'error': 'Video not found'}), 404
    return jsonify({'message': 'Video deleted'})
