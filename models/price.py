from datetime import datetime

import peewee

from .product import Product
from .database import MODEL_DB


class Price(peewee.Model):
    """Model for products"""

    class Meta:
        db_table = 'prices'
        database = MODEL_DB

    price = peewee.DecimalField(decimal_places=3)
    created_at = peewee.DateTimeField(default=datetime.now)

    product = peewee.ForeignKeyField(
        Product, to_field='product_id', related_name='prices', on_delete='CASCADE'
    )
