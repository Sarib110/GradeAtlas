import re
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.models import User

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def success_response(data=None, message='Success', code=200):
    return jsonify({'success': True, 'message': message, 'data': data, 'error': None}), code


def error_response(message='Error occurred', code=400, error=None):
    return jsonify({'success': False, 'message': message, 'data': None, 'error': error or message}), code


def get_json_payload():
    payload = request.get_json(silent=True)
    if payload is None:
        return None, error_response('Invalid JSON payload.', 400, 'invalid_payload')
    return payload, None


def validate_required(data, fields):
    for field in fields:
        if field not in data or data[field] is None or data[field] == '':
            return False, field
    return True, None


def validate_email(email):
    return isinstance(email, str) and EMAIL_REGEX.match(email)


def validate_numbers(payload, keys):
    for key in keys:
        if key not in payload:
            return False, key
        value = payload.get(key)
        try:
            float(value)
        except (TypeError, ValueError):
            return False, key
    return True, None


def get_current_user():
    verify_jwt_in_request(optional=True)
    identity = get_jwt_identity()
    if identity is None:
        return None
    return User.query.get(identity)


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as error:
            return error_response(str(error), 401, 'authorization_required')

        user = get_current_user()
        if not user:
            return error_response('User not found.', 404, 'user_not_found')
        return f(user, *args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return error_response('Invalid or expired token.', 401, 'authorization_required')
        if user.role != 'admin':
            return error_response('Admin access required.', 403, 'admin_required')
        return f(*args, **kwargs)

    return decorated
