import redis.asyncio as redis
import os
from typing import Optional

class RedisManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def init_redis(self):
        """Инициализация Redis подключения"""
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
    
    async def close_redis(self):
        """Закрытие подключения"""
        if self.redis:
            await self.redis.close()
    
    async def ping(self):
        """Проверка подключения"""
        try:
            return await self.redis.ping()
        except Exception:
            return False

redis_manager = RedisManager()
def get_redis():
    return redis_manager.redis