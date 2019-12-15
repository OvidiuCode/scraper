import aiohttp
import asyncio
from bs4 import BeautifulSoup

from models.product import Product
from models.database import OBJ_MANAGER


class Scraper:

    BASE_URL = 'https://www.emag.ro/'
    ITEMS = ['laptopuri', 'telefoane-mobile']

    ITEM_CLASS = 'card-section-wrapper js-section-wrapper'
    BUTTON_CLASS = 'btn btn-sm btn-primary btn-emag yeahIWantThisProduct'
    LINK_CLASS = 'product-title js-product-url'
    OLD_PRICE_CLASS = 'product-old-price'
    NEW_PRICE_CLASS = 'product-new-price'
    NEXT_PAGE_CLASS = 'js-change-page'

    def __init__(self):
        self._session = None

    # Add wait param and ayncio.sleep call to make this as a Task Queue
    async def work(self):
        all_pages = await self.get_all_pages()
        pages = [self.scrape_page(page) for page in all_pages]
        await asyncio.gather(*pages)
        # await asyncio.sleep(wait)

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

            for number in range(2, max_page_number + 1):
                temp_url = self.BASE_URL + item + '/p' + str(number) + '/c'
                pages.append(temp_url)

            self._session.close()
            self._session = None

        return pages

    async def scrape_page(self, page):
        # Get page products
        items = await self.get_page_items(page)
        products = await self.get_products(items)

        # Async insert products in DB
        await OBJ_MANAGER.execute(Product.insert_many(products))

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
        products = []
        for item in items:
            product_id = item.find('button', class_=cls.BUTTON_CLASS)
            if product_id:
                product_id = product_id['data-offer-id']
            else:
                continue

            link = item.find('a', class_=cls.LINK_CLASS).attrs['href']
            title = item.find('a', class_=cls.LINK_CLASS).attrs['title']

            price_item = item.find('p', class_=cls.NEW_PRICE_CLASS).get_text()
            price = float(price_item.split()[0]) if price_item else 0.0

            products.append(
                {
                    'title': title,
                    'link': link,
                    'product_id': product_id,
                    'price': price,
                }
            )

        return products

    async def get_session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()

        return self._session
