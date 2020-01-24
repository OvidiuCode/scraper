from fastapi import FastAPI, Form, Header
from starlette.middleware.cors import CORSMiddleware
import urllib.parse
import html

from models.database import MODEL_DB
from models.alert import Alert
from models.product import Product
from models.price import Price

from scraper import Scraper

app = FastAPI()

origins = ["http://localhost:8080", "http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    product.title = product.title.split(',')[0]

    return {
        "status_code": status_code,
        "product": product.__dict__['__data__'],
        'prices': prices[:7],
        'max_price': max(all_prices),
        'min_price': min(all_prices),
    }


@app.get("/deals/")
async def get_best_deals():
    best_deals = MODEL_DB.execute_sql(
        """
        SELECT prd.id , prd.product_id , prd.title , prd.link , prd.price , prd.created_at,
          (SELECT second_min.price - prd.price
           FROM
             (SELECT prc2.price
              FROM prices AS prc2
              WHERE prc2.product_id = prd.product_id
              ORDER BY prc2.price DESC
              OFFSET 1 LIMIT 1) AS second_min) AS price_diff
        FROM products AS prd
        INNER JOIN prices AS prc ON (prc.product_id = prd.product_id)
        GROUP BY prd.id
        HAVING (prd.price = MIN(prc.price) and count(prc.price) > 1)
        ORDER BY price_diff DESC
        LIMIT 5;
        """
    )

    products = []
    for deal in best_deals:
        products.append(
            {
                'title': html.unescape(deal[2].split(',')[0]),
                'link': deal[3],
                'price': float(deal[4]),
            }
        )

    return {'status_code': 200, 'products': products}


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
