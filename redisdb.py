import redis
import os


def register_redis_db():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "127.0.0.1"),
        port=os.getenv("REDIS_PORT", 6379),
        db=os.getenv("REDIS_DB", 0),
        password=os.getenv("REDIS_PASSWORD", "foobared"),
        decode_responses=True
    )
