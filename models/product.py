from datetime import datetime

import peewee

from .database import MODEL_DB


class Product(peewee.Model):
    """Model for products"""

    class Meta:
        db_table = 'products'
        database = MODEL_DB

    product_id = peewee.CharField(unique=True, index=True)
    title = peewee.TextField(index=True)
    link = peewee.TextField()
    price = peewee.DecimalField(decimal_places=3)
    created_at = peewee.DateTimeField(default=datetime.now)
