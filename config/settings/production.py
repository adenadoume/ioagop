from .base import *  # noqa
import os
import dj_database_url
DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY missing")

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS","").split(",") if h.strip()]

def _originify(host: str) -> str:
    if not host: return ""
    if host.startswith("http://") or host.startswith("https://"): return host
    return f"https://{host}"
CSRF_TRUSTED_ORIGINS = [_originify(h) for h in ALLOWED_HOSTS if h]

DATABASES = {
    "default": dj_database_url.config(env="DATABASE_URL", conn_max_age=600, ssl_require=False)
}
if not DATABASES["default"]:
    raise RuntimeError("DATABASE_URL not configured")

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "KEY_PREFIX": os.environ.get("PROJECT_SLUG","app"),
        }
    }

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
FORCE_HTTPS = os.environ.get("FORCE_HTTPS","1") in ("1","true","True")
SESSION_COOKIE_SECURE = FORCE_HTTPS
CSRF_COOKIE_SECURE = FORCE_HTTPS
SECURE_SSL_REDIRECT = FORCE_HTTPS

DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DATA_UPLOAD_MAX_MEMORY_SIZE", str(100*1024*1024)))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("FILE_UPLOAD_MAX_MEMORY_SIZE", str(10*1024*1024)))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
