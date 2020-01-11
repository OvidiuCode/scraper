import peewee

from helper import Helper

config = Helper.get_config()['database']

# Define async database
MODEL_DB = peewee.PostgresqlDatabase(
    config['name'],
    host=config['host'],
    user=config['user'],
    password=config['password'],
)
