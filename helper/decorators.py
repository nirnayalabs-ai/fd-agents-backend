import functools
import hashlib
import json
from django.core.cache import cache

def redis_cache(timeout=3600):
    """Decorator to cache function results in Redis without encryption."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # Generate unique cache key based on function args
            cache_key = f"{func.__name__}:{json.dumps(args, default=str)}:{json.dumps(kwargs, default=str)}"
            cache_key_hash = hashlib.sha256(cache_key.encode()).hexdigest()

            # Try fetching from cache
            cached_result = cache.get(cache_key_hash)
            if cached_result is not None:
                print(f"✅ CACHE HIT: {func.__name__} | Key: {cache_key_hash}")
                return cached_result

            # Compute the result if cache miss
            print(f"⚠️ CACHE MISS: {func.__name__} | Key: {cache_key_hash}. Computing result...")
            result = func(*args, **kwargs)

            # Store in Redis
            cache.set(cache_key_hash, result, timeout)
            print(f"💾 CACHE SET: {func.__name__} | Key: {cache_key_hash}")

            return result

        return wrapper
    return decorator
