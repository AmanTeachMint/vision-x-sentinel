"""Classrooms API: GET list, GET by id."""
from flask import Blueprint, jsonify

from app.db.store import get_all_classrooms, get_classroom_by_id

bp = Blueprint('classrooms', __name__, url_prefix='/api/classrooms')


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def list_classrooms():
    """GET /api/classrooms — return all classrooms."""
    classrooms = get_all_classrooms()
    return jsonify(classrooms)


@bp.route('/<classroom_id>', methods=['GET'])
def get_classroom(classroom_id):
    """GET /api/classrooms/<id> — return one classroom or 404."""
    classroom = get_classroom_by_id(classroom_id)
    if classroom is None:
        return jsonify({'error': 'Classroom not found'}), 404
    return jsonify(classroom)
