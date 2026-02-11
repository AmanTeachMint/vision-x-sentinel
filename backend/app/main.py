"""Main Flask application."""
import os
from flask import Flask, request, Response

from app.config import Config

try:
    from flask_cors import CORS
    HAS_FLASK_CORS = True
except ImportError:
    HAS_FLASK_CORS = False

def create_app():
    """Create and configure Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    if HAS_FLASK_CORS:
        CORS(app, origins=[Config.CORS_ORIGIN])
    else:
        @app.before_request
        def handle_preflight():
            """Handle OPTIONS preflight requests for CORS."""
            if request.method == 'OPTIONS':
                response = Response()
                response.headers['Access-Control-Allow-Origin'] = Config.CORS_ORIGIN
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                return response
        
        @app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = Config.CORS_ORIGIN
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            return response
    
    # Register API blueprints
    from app.api import classrooms, alerts, sentinel, videos
    app.register_blueprint(classrooms.bp)
    app.register_blueprint(alerts.bp)
    app.register_blueprint(sentinel.bp)
    app.register_blueprint(videos.bp)
    
    @app.route('/')
    def hello():
        return {'message': 'Vision X Sentinel API is running', 'status': 'ok'}
    
    return app
