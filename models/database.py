import peewee_async

# Define async database
MODEL_DB = peewee_async.PostgresqlDatabase(
    'licenta', host='localhost', user='ovidiu', password='Rnjnr1PJpMPK0XG!R$ZB#SAa'
)
MODEL_DB.set_allow_sync(False)

# Create async models manager
OBJ_MANAGER = peewee_async.Manager(MODEL_DB)
