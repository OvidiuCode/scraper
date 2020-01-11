from fastapi import FastAPI
from pydantic import BaseModel

from models.alert import Alert
from models.product import Product

from scraper import Scraper

app = FastAPI()


class AlertParams(BaseModel):
    link: str
    email: str
    price: float


@app.post("/alert/")
async def add_alert(alert: AlertParams):

    scraper = Scraper(custom_page=alert.link)
    status_code, message = await scraper.work()

    if status_code != 200:
        return {"status_code": 404, "message": message}

    Alert.get_or_create(
        link=alert.link, email=alert.email, price=alert.price, satisfied=False
    )

    return {"status_code": 200, "message": "Alert created!"}


@app.get("/product/")
async def search_product(link: str):
    scraper = Scraper(custom_page=link)
    status_code, message = await scraper.work()

    if status_code != 200:
        return {"status_code": 404, "message": message}

    product = Product.select().where(Product.product_id == message).first()

    return {
        "status_code": status_code,
        "product": product.__dict__['__data__'],
        'prices': product.prices.dicts()[:],
    }
