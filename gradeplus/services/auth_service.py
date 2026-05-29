import re
from datetime import timedelta
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash
from database.db import db
from models.models import User

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
ROLE_OPTIONS = {'user', 'admin'}


def _get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def validate_email(email):
    return isinstance(email, str) and EMAIL_REGEX.match(email)


def validate_password_strength(password):
    value = str(password or '')
    return len(value) >= 8


def validate_registration_payload(payload):
    if not payload:
        return False, 'invalid_payload'
    if 'username' not in payload or not isinstance(payload['username'], str) or not payload['username'].strip():
        return False, 'username'
    if 'email' not in payload or not validate_email(payload['email']):
        return False, 'email'
    if 'password' not in payload or not validate_password_strength(payload['password']):
        return False, 'password'
    return True, None


def validate_login_payload(payload):
    if not payload:
        return False, 'invalid_payload'
    if 'email' not in payload or not validate_email(payload['email']):
        return False, 'email'
    if 'password' not in payload or not payload['password']:
        return False, 'password'
    return True, None


def create_user(username, email, password, role='user'):
    user = User(username=username.strip(), email=email.lower())
    user.set_password(password)
    user.role = role if role in ROLE_OPTIONS else 'user'
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email, password):
    user = User.query.filter_by(email=email.lower()).first()
    if user and user.check_password(password):
        return user
    return None


def generate_tokens(user_id):
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return {'access_token': access_token, 'refresh_token': refresh_token}


def generate_password_reset_token(user_id, expires_sec=3600):
    serializer = _get_serializer()
    return serializer.dumps({'user_id': user_id}, salt='password-reset')


def verify_password_reset_token(token, max_age=3600):
    serializer = _get_serializer()
    try:
        data = serializer.loads(token, salt='password-reset', max_age=max_age)
        return data.get('user_id'), None
    except SignatureExpired:
        return None, 'Token has expired.'
    except BadSignature:
        return None, 'Invalid password reset token.'
