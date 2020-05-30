import asyncio
import uvloop

from scraper import Scraper
from alert_dispatcher import AlertDispatcher

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    scraper = Scraper()
    alert_dispatcher = AlertDispatcher()

    loop.run_until_complete(scraper.work())
    # loop.run_until_complete(alert_dispatcher.work())

    # loop.create_task(scraper.work())
    # loop.run_forever()
