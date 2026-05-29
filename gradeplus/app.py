import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from werkzeug.exceptions import HTTPException
from config import Config
from database.db import db
from routes.routes import api as main_api
from routes.auth_routes import auth_api
from routes.admin_routes import admin_api
from utils.logger import setup_logger
from utils.token_blocklist import is_token_revoked

cache = Cache()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

    db.init_app(app)
    Migrate(app, db)
    Limiter(key_func=get_remote_address, app=app, default_limits=[app.config.get('RATELIMIT_DEFAULT')], storage_uri=app.config.get('RATELIMIT_STORAGE_URI'))

    # Configure caching: prefer Redis if configured, fallback to simple in-memory cache
    if app.config.get('CACHE_REDIS_URL'):
        cache_config = {'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL')}
    else:
        cache_config = {'CACHE_TYPE': 'SimpleCache'}
    cache.init_app(app, config=cache_config)

    app.register_blueprint(main_api, url_prefix='/api')
    app.register_blueprint(auth_api, url_prefix='/api')
    app.register_blueprint(admin_api, url_prefix='/api')

    setup_logger(app)

    @app.before_request
    def log_request_info():
        app.logger.info('%s %s from %s', request.method, request.path, request.remote_addr)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({'success': False, 'message': err.description, 'data': None, 'error': err.name}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception(err)
        return jsonify({'success': False, 'message': 'Internal server error.', 'data': None, 'error': str(err)}), 500

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload['jti'])

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'Token has been revoked.', 'data': None, 'error': 'token_revoked'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'Token has expired.', 'data': None, 'error': 'token_expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'success': False, 'message': 'Invalid token.', 'data': None, 'error': 'invalid_token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'success': False, 'message': 'Request does not contain an access token.', 'data': None, 'error': 'authorization_required'}), 401

    return app


if __name__ == '__main__':
    app = create_app()
    app.logger.setLevel(logging.INFO)
    app.logger.info('GradeAtlas running at http://localhost:5000')
    app.run(host='0.0.0.0', port=5000)
