from flask import Blueprint
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt, get_jwt_identity
)
from database.db import db
from models.models import User
from services.auth_service import (
    authenticate_user, create_user, generate_password_reset_token,
    verify_password_reset_token, validate_login_payload,
    validate_registration_payload, validate_email, validate_password_strength
)
from utils.helpers import (
    error_response, get_json_payload, success_response,
    validate_required
)
from utils.token_blocklist import revoke_token

auth_api = Blueprint('auth_api', __name__)


@auth_api.route('/auth/register', methods=['POST'])
def register():
    payload, error = get_json_payload()
    if error:
        return error

    valid, field = validate_registration_payload(payload)
    if not valid:
        return error_response(f'Invalid or missing field: {field}', 400)

    if User.query.filter_by(email=payload['email'].lower()).first():
        return error_response('Email already registered.', 409)

    if User.query.filter_by(username=payload['username'].strip()).first():
        return error_response('Username taken.', 409)

    user = create_user(payload['username'], payload['email'], payload['password'])
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return success_response({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }, 'Account created!', 201)


@auth_api.route('/auth/login', methods=['POST'])
def login():
    payload, error = get_json_payload()
    if error:
        return error

    valid, field = validate_login_payload(payload)
    if not valid:
        return error_response(f'Invalid or missing field: {field}', 400)

    user = authenticate_user(payload['email'], payload['password'])
    if not user:
        return error_response('Invalid credentials.', 401)

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return success_response({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }, 'Login successful!')


@auth_api.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return error_response('User identity missing from refresh token.', 401)
    new_token = create_access_token(identity=current_user_id)
    return success_response({'access_token': new_token}, 'Access token refreshed.')


@auth_api.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    # determine token type and revoke with appropriate expiry
    token_type = get_jwt().get('type')
    revoke_token(jti, token_type=token_type)
    return success_response(None, 'Access token revoked.')


@auth_api.route('/auth/logout/refresh', methods=['POST'])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()['jti']
    token_type = get_jwt().get('type')
    revoke_token(jti, token_type=token_type)
    return success_response(None, 'Refresh token revoked.')


@auth_api.route('/auth/request-password-reset', methods=['POST'])
def request_password_reset():
    payload, error = get_json_payload()
    if error:
        return error

    ok, missing = validate_required(payload, ['email'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    if not validate_email(payload['email']):
        return error_response('Email must be valid.', 400)

    user = User.query.filter_by(email=payload['email'].lower()).first()
    if not user:
        return success_response(None, 'If the email exists, a password reset link has been sent.')

    reset_token = generate_password_reset_token(user.id)
    # In a real deployment this token would be emailed.
    return success_response({'reset_token': reset_token}, 'Password reset token created.')


@auth_api.route('/auth/reset-password', methods=['POST'])
def reset_password():
    payload, error = get_json_payload()
    if error:
        return error

    ok, missing = validate_required(payload, ['token', 'password'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    if not validate_password_strength(payload['password']):
        return error_response('Password must be at least 8 characters long.', 400)

    user_id, token_error = verify_password_reset_token(payload['token'])
    if token_error:
        return error_response(token_error, 400)

    user = User.query.get(user_id)
    if not user:
        return error_response('User not found.', 404)

    user.set_password(payload['password'])
    db.session.commit()
    return success_response(None, 'Password updated successfully.')
