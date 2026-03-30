"""
Authentication API
POST /api/auth/login  — verify credentials, return HMAC token + role
"""

import hmac
import hashlib

from flask import Blueprint, request, jsonify, current_app

auth_bp = Blueprint('auth', __name__)

# Maps role name → (config key for login, config key for password)
_USERS = {
    'admin': ('ADMIN_LOGIN', 'ADMIN_PASSWORD'),
    'demo':  ('DEMO_LOGIN',  'DEMO_PASSWORD'),
}


def _make_token(secret: str, username: str, password: str) -> str:
    """Deterministic HMAC-SHA256 token — no DB needed."""
    return hmac.new(
        secret.encode(),
        f"{username}:{password}".encode(),
        hashlib.sha256
    ).hexdigest()


def _valid_token(cfg, token: str) -> bool:
    """Check token against every known user."""
    for login_key, pass_key in _USERS.values():
        expected = _make_token(cfg['SECRET_KEY'], cfg[login_key], cfg[pass_key])
        if hmac.compare_digest(token, expected):
            return True
    return False


@auth_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    cfg = current_app.config
    for role, (login_key, pass_key) in _USERS.items():
        if username == cfg[login_key] and password == cfg[pass_key]:
            token = _make_token(cfg['SECRET_KEY'], username, password)
            return jsonify({'token': token, 'role': role, 'username': username})

    return jsonify({'error': 'Неверный логин или пароль'}), 401
