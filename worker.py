import asyncio
import uvloop

from workers.scraper import Scraper
from workers.alert_dispatcher import AlertDispatcher

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    scraper = Scraper()
    alert_dispatcher = AlertDispatcher()

    loop.create_task(scraper.work())
    loop.create_task(alert_dispatcher.work())
    loop.run_forever()
