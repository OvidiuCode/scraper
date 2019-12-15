from datetime import datetime

import peewee

from .database import MODEL_DB


class Product(peewee.Model):
    """Model for products"""

    class Meta:
        db_table = 'products'
        database = MODEL_DB

    title = peewee.TextField(index=True)
    link = peewee.TextField()
    product_id = peewee.CharField()
    price = peewee.DecimalField()
    created_at = peewee.DateTimeField(default=datetime.now)
