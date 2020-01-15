from fastapi import FastAPI, Form, Header
import urllib.parse

from models.alert import Alert
from models.product import Product
from models.price import Price

from scraper import Scraper

app = FastAPI()


@app.post("/alert/")
async def add_alert(
    email: str = Form(default=None),
    price: int = Form(default=None),
    referer: str = Header(default=None),
):

    decoded_link = urllib.parse.unquote(referer.split('=')[1])
    scraper = Scraper(custom_page=decoded_link)
    status_code, message = await scraper.work()

    if status_code != 200:
        return {"status_code": 404, "message": message}

    Alert.get_or_create(
        product_id=message, link=decoded_link, email=email, price=price, satisfied=False
    )

    return {"status_code": 200, "message": "Alert created!"}


@app.get("/product/")
async def search_product(link: str):
    decoded_link = urllib.parse.unquote(link)

    scraper = Scraper(custom_page=decoded_link)
    status_code, response = await scraper.work()

    if status_code != 200:
        return {"status_code": 404, "message": response}

    product = Product.select().where(Product.product_id == response).first()
    prices = product.prices.order_by(Price.created_at.desc()).dicts()[:]

    all_prices = [item['price'] for item in prices]
    for price in prices:
        price['created_at'] = price['created_at'].date()

    return {
        "status_code": status_code,
        "product": product.__dict__['__data__'],
        'prices': prices[:7],
        'max_price': max(all_prices),
        'min_price': min(all_prices),
    }
