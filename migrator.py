import sys

from models.product import Product
from models.alert import Alert
from models.price import Price
from models.database import MODEL_DB

all_models = [Product, Alert, Price]
MODEL_DB.set_allow_sync(True)


def up():
    # Migrate all products
    for model in all_models:
        if not model.table_exists():
            model.create_table()


def down():
    for model in all_models:
        if model.table_exists():
            model.drop_table()


if __name__ == "__main__":
    if not sys.argv:
        print("You must provide an argument: up or down.")
    direction = sys.argv[1]
    if direction.lower() == 'up':
        up()
    elif direction.lower() == 'down':
        down()
    else:
        print("Unknown command. Available commands are: up or down")
