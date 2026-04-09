import redis
from redis.exceptions import ConnectionError

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=False,
    socket_connect_timeout=1,
    socket_timeout=1
)

def cache_get(key):
    try:
        return redis_client.get(key)
    except ConnectionError:
        return None

def cache_set(key, value, ex=60):
    try:
        redis_client.set(key, value, ex=ex)
    except ConnectionError:
        pass

def cache_delete(key):
    try:
        redis_client.delete(key)
    except ConnectionError:
        pass