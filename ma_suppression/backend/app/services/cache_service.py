from functools import wraps
import json
import os
import time
from typing import Any, Callable, Dict, Optional
import pickle
import hashlib

class CacheService:
    """Service for handling both memory and disk caching."""
    
    def __init__(self, cache_dir: str = "/tmp/ma_suppression_cache"):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key."""
        # Convert non-serializable objects to their string representation
        def make_serializable(obj):
            if hasattr(obj, '__dict__'):
                return str(obj.__class__.__name__)
            if isinstance(obj, (list, tuple)):
                return [make_serializable(x) for x in obj]
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            return obj

        key_data = {
            'args': make_serializable(args),
            'kwargs': make_serializable(kwargs)
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"{prefix}_{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key."""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def get_from_memory(self, key: str) -> Optional[Any]:
        """Get item from memory cache if not expired."""
        cache_item = self.memory_cache.get(key)
        if not cache_item:
            return None
            
        if time.time() > cache_item['expires']:
            del self.memory_cache[key]
            return None
            
        return cache_item['data']
    
    def set_in_memory(self, key: str, value: Any, ttl: int = 300):
        """Set item in memory cache with TTL in seconds."""
        self.memory_cache[key] = {
            'data': value,
            'expires': time.time() + ttl
        }
    
    def get_from_disk(self, key: str) -> Optional[Any]:
        """Get item from disk cache if not expired."""
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'rb') as f:
                cache_item = pickle.load(f)
                
            if time.time() > cache_item['expires']:
                os.remove(cache_path)
                return None
                
            return cache_item['data']
        except Exception as e:
            print(f"Error reading cache file {cache_path}: {e}")
            return None
    
    def set_on_disk(self, key: str, value: Any, ttl: int = 86400):
        """Set item in disk cache with TTL in seconds (default 24h)."""
        cache_path = self._get_cache_path(key)
        cache_item = {
            'data': value,
            'expires': time.time() + ttl
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_item, f)
        except Exception as e:
            print(f"Error writing cache file {cache_path}: {e}")
    
    def cache_method(self, prefix: str, ttl_memory: int = 300, ttl_disk: int = 86400):
        """Decorator for caching method results in both memory and disk."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._get_cache_key(prefix, *args, **kwargs)
                
                # Try memory cache first
                result = self.get_from_memory(cache_key)
                if result is not None:
                    print(f"Cache hit (memory): {cache_key}")
                    return result
                
                # Try disk cache
                result = self.get_from_disk(cache_key)
                if result is not None:
                    print(f"Cache hit (disk): {cache_key}")
                    # Also cache in memory for faster subsequent access
                    self.set_in_memory(cache_key, result, ttl_memory)
                    return result
                
                # Cache miss - call original function
                print(f"Cache miss: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Cache result in both memory and disk
                self.set_in_memory(cache_key, result, ttl_memory)
                self.set_on_disk(cache_key, result, ttl_disk)
                
                return result
            return wrapper
        return decorator

# Global cache service instance
cache_service = CacheService()
