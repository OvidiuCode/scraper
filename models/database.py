import peewee
from redis import StrictRedis
from redis_cache import RedisCache

from helper import Helper

config = Helper.get_config()['database']

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
