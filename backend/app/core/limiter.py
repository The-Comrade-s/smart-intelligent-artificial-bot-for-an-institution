"""
Rate limiting via slowapi (Redis-free, in-memory by default; point
STORAGE_URI at Redis in production for multi-instance consistency).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])
