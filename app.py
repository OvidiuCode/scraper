from fastapi import FastAPI, Form, Header
from starlette.middleware.cors import CORSMiddleware
import urllib.parse
import html

from models.database import MODEL_DB, cache
from models.alert import Alert
from models.product import Product
from models.price import Price

from scraper import Scraper

app = FastAPI()

origins = ["http://localhost:8080", "http://localhost", "https://ualert.xyz"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BEST_DEALS_TTL = 3 * 60 * 60  # 3 hours in seconds


@app.get("/product/")
async def search_product(link: str):
    decoded_link = urllib.parse.unquote(link)

    scraper = Scraper(custom_page=decoded_link)
    status_code, response = await scraper.work()

    if status_code != 200:
        return {"status_code": status_code, "message": response}

    product = Product.select().where(Product.product_id == response).first()
    prices = product.prices.order_by(Price.created_at.asc()).dicts()[:]

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


@cache.cache(ttl=BEST_DEALS_TTL)
@app.get("/deals/")
async def get_best_deals():
    best_deals = MODEL_DB.execute_sql(
        """
        SELECT prd.title , prd.link , prd.price, 
          (SELECT ((second_min.price - prd.price) / second_min.price * 100)
           FROM
             (SELECT prc2.price
              FROM prices AS prc2
              WHERE prc2.product_id = prd.product_id
              ORDER BY prc2.created_at DESC
              OFFSET 1 LIMIT 1) AS second_min) AS discount
        FROM products AS prd
        INNER JOIN prices AS prc ON (prc.product_id = prd.product_id)
        GROUP BY prd.id
        HAVING (prd.price = MIN(prc.price) and count(prc.price) > 1)
        ORDER BY discount DESC
        LIMIT 5;
        """
    )

    products = []
    for deal in best_deals:
        products.append(
            {
                'title': html.unescape(deal[0].split(',')[0]),
                'link': deal[1],
                'discount': f"{deal[3]:.2f}",
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
