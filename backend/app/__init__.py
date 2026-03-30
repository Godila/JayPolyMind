"""
JayPolyMind Backend - Flask Application Factory
"""

import os
import hmac
import hashlib
import warnings

# Suppress multiprocessing resource_tracker warnings (from third-party libraries like transformers)
# Must be set before all other imports
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request, jsonify
from flask_cors import CORS

from .config import Config
from .utils.logger import setup_logger, get_logger

# Paths that do NOT require a Bearer token
_AUTH_SKIP = {'/health', '/api/auth/login'}

# Same user map as in auth.py (kept in sync)
_AUTH_USERS = {
    'admin': ('ADMIN_LOGIN', 'ADMIN_PASSWORD'),
    'demo':  ('DEMO_LOGIN',  'DEMO_PASSWORD'),
}


def _check_token(cfg, token: str) -> bool:
    for login_key, pass_key in _AUTH_USERS.values():
        expected = hmac.new(
            cfg['SECRET_KEY'].encode(),
            f"{cfg[login_key]}:{cfg[pass_key]}".encode(),
            hashlib.sha256
        ).hexdigest()
        if hmac.compare_digest(token, expected):
            return True
    return False


def create_app(config_class=Config):
    """Flask application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure JSON encoding: ensure Chinese displays directly (not as \uXXXX)
    # Flask >= 2.3 uses app.json.ensure_ascii, older versions use JSON_AS_ASCII config
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False

    # Setup logging
    logger = setup_logger('jaypolymind')

    # Only print startup info in reloader subprocess (avoid printing twice in debug mode)
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process

    if should_log_startup:
        logger.info("=" * 50)
        logger.info("JayPolyMind Backend starting...")
        logger.info("=" * 50)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # --- Initialize Neo4jStorage singleton (DI via app.extensions) ---
    from .storage import Neo4jStorage
    try:
        neo4j_storage = Neo4jStorage()
        app.extensions['neo4j_storage'] = neo4j_storage
        if should_log_startup:
            logger.info("Neo4jStorage initialized (connected to %s)", Config.NEO4J_URI)
    except Exception as e:
        logger.error("Neo4jStorage initialization failed: %s", e)
        # Store None so endpoints can return 503 gracefully
        app.extensions['neo4j_storage'] = None

    # Register simulation process cleanup function (ensure all simulation processes terminate on server shutdown)
    from .services.simulation_runner import SimulationRunner
    SimulationRunner.register_cleanup()
    if should_log_startup:
        logger.info("Simulation process cleanup function registered")

    # Auth middleware — protect all /api/* except the login endpoint
    @app.before_request
    def verify_token():
        # Allow OPTIONS (CORS preflight) and non-API paths through
        if request.method == 'OPTIONS':
            return
        if not request.path.startswith('/api/'):
            return
        if request.path in _AUTH_SKIP:
            return
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        token = auth_header[7:]
        if not _check_token(app.config, token):
            return jsonify({'error': 'Unauthorized'}), 401

    # Request logging middleware
    @app.before_request
    def log_request():
        logger = get_logger('jaypolymind.request')
        logger.debug(f"Request: {request.method} {request.path}")
        if request.content_type and 'json' in request.content_type:
            logger.debug(f"Request body: {request.get_json(silent=True)}")

    @app.after_request
    def log_response(response):
        logger = get_logger('jaypolymind.request')
        logger.debug(f"Response: {response.status_code}")
        return response

    # Register blueprints
    from .api import graph_bp, simulation_bp, report_bp, auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(report_bp, url_prefix='/api/report')

    # Health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'JayPolyMind Backend'}

    if should_log_startup:
        logger.info("JayPolyMind Backend startup complete")

    return app

