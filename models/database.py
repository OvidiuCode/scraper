import peewee
from redis import StrictRedis
from redis_cache import RedisCache

from dynaconf import settings

config = settings.DATABASE

# Define async database
MODEL_DB = peewee.PostgresqlDatabase(
    config['name'],
    host=config['host'],
    user=config['user'],
    password=config['password'],
    autorollback=True,
)

redis_client = StrictRedis(host="redis", decode_responses=True)
cache = RedisCache(redis_client=redis_client)
