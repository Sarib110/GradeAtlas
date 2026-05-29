from datetime import datetime
import os
from flask import current_app

try:
    import redis
except Exception:
    redis = None

# In-memory fallback
BLOCKLIST = set()


def _get_redis_client():
    url = None
    if current_app:
        url = current_app.config.get('CACHE_REDIS_URL')
    if not url:
        url = os.getenv('CACHE_REDIS_URL')
    if not url or not redis:
        return None
    return redis.from_url(url)


def revoke_token(jti, token_type=None, expires=None):
    """Revoke a JWT by JTI. If Redis is available, store with expiry, otherwise use in-memory set."""
    client = _get_redis_client()
    if client:
        key = f'blocklist:{jti}'
        ttl = expires
        if ttl is None and current_app:
            if token_type == 'refresh':
                ttl = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
            else:
                ttl = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        try:
            if ttl:
                client.set(key, '1', ex=int(ttl))
            else:
                client.set(key, '1')
            return True
        except Exception:
            # fallback to in-memory on any redis error
            BLOCKLIST.add(jti)
            return False

    # In-memory fallback
    BLOCKLIST.add(jti)
    return True


def is_token_revoked(jti):
    client = _get_redis_client()
    if client:
        try:
            return client.exists(f'blocklist:{jti}') == 1
        except Exception:
            return jti in BLOCKLIST
    return jti in BLOCKLIST


def get_blocklist_snapshot():
    client = _get_redis_client()
    if client:
        try:
            keys = client.keys('blocklist:*')
            return {'revoked_count': len(keys), 'last_updated': datetime.utcnow().isoformat()}
        except Exception:
            pass
    return {'revoked_count': len(BLOCKLIST), 'last_updated': datetime.utcnow().isoformat()}
