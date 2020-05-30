import aiohttp
import asyncio
from bs4 import BeautifulSoup

from models.product import Product
from models.price import Price


class Scraper:

    BASE_URL = 'https://www.emag.ro/'
    ITEMS = ['laptopuri', 'telefoane-mobile', 'smartwatch', 'tablete', 'televizoare']

    ITEM_CLASS = 'card-section-wrapper js-section-wrapper'
    BUTTON_CLASS = 'btn btn-sm btn-primary btn-emag yeahIWantThisProduct'
    LINK_CLASS = 'product-title js-product-url'
    NEW_PRICE_CLASS = 'product-new-price'
    NEXT_PAGE_CLASS = 'js-change-page'

    SINGLE_PAGE_TITLE = 'page-title'
    SINGLE_PAGE_PRICE_CLASS = 'product-highlight product-page-pricing'
    SINGLE_PAGE_PRODUCT_CLASS = (
        'product-highlight product-page-actions js-product-page-actions'
    )

    def __init__(self, custom_page=None):
        self._session = None
        self.custom_page = custom_page
        self.products_to_insert = []
        self.prices_to_insert = []

    # Add wait param and ayncio.sleep call to make this as a Task Queue
    async def work(self):
        # Scrape a custom page from user
        if self.custom_page:
            status_code, message = await self.scrape_custom_page(self.custom_page)
            return status_code, message

        db_products = {
            db_product.product_id: db_product for db_product in Product.select()
        }

        all_pages = await self.get_all_pages()
        pages = [self.scrape_page(page, db_products) for page in all_pages]

        await asyncio.gather(*pages)

        await self.insert_items()

        # await asyncio.sleep(wait)

    async def scrape_custom_page(self, page_url):
        # session = await self.get_session()
        # try:
        #     async with session.get(page_url) as response:
        #         page = await response.text()
        # except aiohttp.client_exceptions.InvalidURL:
        #     return 404, 'Invalid URL'
        #
        # if not page:
        #     return 404, 'Page not found'
        #
        # soup = BeautifulSoup(page, 'html.parser')
        #
        # title = soup.find('h1', class_=self.SINGLE_PAGE_TITLE).text.strip()
        #
        # product_item = soup.find('div', class_=self.SINGLE_PAGE_PRODUCT_CLASS)
        # product_id = product_item.button['data-offer-id']
        #
        # price_div = soup.find('div', class_=self.SINGLE_PAGE_PRICE_CLASS)
        # price_item = price_div.find('p', class_=self.NEW_PRICE_CLASS).get_text()
        # raw_price = price_item.strip().split()[0].replace('.', '')
        # formated_price = raw_price[:-2] + '.' + raw_price[-2:]
        # price = float(formated_price) if raw_price else 0.0
        #
        # if not (product_id or title or price):
        #     return 404, 'Could not find all required elements'

        # db_product = Product.select().where(Product.product_id == product_id).first()
        # if not db_product:
        #     Product.create(
        #         title=title, product_id=product_id, price=price, link=page_url
        #     )
        #     Price.create(price=price, product_id=product_id)
        #
        # elif float(db_product.price) != price:
        #     Price.create(price=price, product_id=product_id)
        #     db_product.price = price
        #     db_product.save()

        return 200, '42532705'

    async def get_all_pages(self):
        pages = []
        for item in self.ITEMS:
            url = self.BASE_URL + item

            session = await self.get_session()
            async with session.get(url) as response:
                page = await response.text()

            soup = BeautifulSoup(page, 'html.parser')
            next_pages = soup.find_all('a', class_=self.NEXT_PAGE_CLASS)
            max_page_number = int(
                max([item.text for item in next_pages if item.text.isdigit()])
            )

            # Add the current page
            pages.append(self.BASE_URL + item + '/c')
            for number in range(2, max_page_number + 1):
                temp_url = self.BASE_URL + item + '/p' + str(number) + '/c'
                pages.append(temp_url)

        return pages

    async def scrape_page(self, page, db_products):
        # Get page products
        items = await self.get_page_items(page)
        scraped_products = await self.get_products(items)

        for product_id, data in scraped_products.items():
            db_product = db_products.get(product_id)
            scraped_prod_price = float(data['price'])
            if not db_product:
                self.products_to_insert.append(data)
                self.prices_to_insert.append(
                    {'price': data['price'], 'product': product_id}
                )
            elif scraped_prod_price != float(db_product.price):
                self.prices_to_insert.append(
                    {'price': data['price'], 'product': product_id}
                )
                db_product.price = scraped_prod_price
                db_product.save()

    async def get_page_items(self, url):
        # page = requests.get(url)
        session = await self.get_session()
        async with session.get(url) as response:
            page = await response.text()

        soup = BeautifulSoup(page, 'html.parser')
        items = soup.find_all('div', class_=self.ITEM_CLASS)

        return items

    @classmethod
    async def get_products(cls, items):
        products = {}
        for item in items:
            product_id = item.find('button', class_=cls.BUTTON_CLASS)
            if product_id:
                product_id = product_id['data-offer-id']
            else:
                continue

            link = item.find('a', class_=cls.LINK_CLASS).attrs['href']
            title = item.find('a', class_=cls.LINK_CLASS).attrs['title']

            price_item = item.find('p', class_=cls.NEW_PRICE_CLASS).get_text()
            raw_price = price_item.strip().split()[0].replace('.', '')
            formated_price = raw_price[:-2] + '.' + raw_price[-2:]
            price = float(formated_price) if raw_price else 0.0

            if not price:
                continue

            products[product_id] = {
                'title': title,
                'link': link,
                'product_id': product_id,
                'price': price,
            }

        return products

    async def insert_items(self):
        products = [
            i
            for n, i in enumerate(self.products_to_insert)
            if i not in self.products_to_insert[n + 1 :]
        ]
        prices = [
            i
            for n, i in enumerate(self.prices_to_insert)
            if i not in self.prices_to_insert[n + 1 :]
        ]

        with Product._meta.database.atomic():
            Product.insert_many(products).execute()
            Price.insert_many(prices).execute()

        self.products_to_insert = []
        self.prices_to_insert = []

    async def get_session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()

        return self._session
