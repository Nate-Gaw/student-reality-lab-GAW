from __future__ import annotations

import json
import os
import time
from typing import Any, Optional

import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TTL_SECONDS = 3600


class RedisCache:
    def __init__(self) -> None:
        self._client = None
        self._memory_cache: dict[str, tuple[float, Any]] = {}
        try:
            self._client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            self._client.ping()
        except redis.RedisError:
            self._client = None

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        if key in self._memory_cache:
            expires_at, value = self._memory_cache[key]
            if expires_at >= now:
                return value
            self._memory_cache.pop(key, None)

        if not self._client:
            return None

        try:
            raw = self._client.get(key)
        except redis.RedisError:
            return None

        if raw is None:
            return None

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    def set(self, key: str, value: Any, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        expires_at = time.time() + ttl_seconds
        self._memory_cache[key] = (expires_at, value)

        if not self._client:
            return

        try:
            self._client.setex(key, ttl_seconds, json.dumps(value))
        except redis.RedisError:
            return


cache = RedisCache()
