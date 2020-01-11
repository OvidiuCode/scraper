from datetime import datetime

import peewee

from .product import Product
from .database import MODEL_DB


class Alert(peewee.Model):
    """Model for alerts"""

    class Meta:
        db_table = 'alerts'
        database = MODEL_DB

    link = peewee.TextField()
    email = peewee.TextField()
    price = peewee.DecimalField()
    satisfied = peewee.BooleanField(default=False, index=True)
    created_at = peewee.DateTimeField(default=datetime.now)

    product = peewee.ForeignKeyField(
        Product, related_name='alerts', on_delete='CASCADE',
    )
