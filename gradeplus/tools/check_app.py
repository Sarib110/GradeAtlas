from app import create_app
app = create_app()
print('DEBUG=', app.config.get('DEBUG'))
print('DB URI=', app.config.get('SQLALCHEMY_DATABASE_URI'))
print('RATE LIMIT URI=', app.config.get('RATELIMIT_STORAGE_URI'))
print('CACHE URL=', app.config.get('CACHE_REDIS_URL'))
print('JWT ACCESS EXPIRES=', app.config.get('JWT_ACCESS_TOKEN_EXPIRES'))
