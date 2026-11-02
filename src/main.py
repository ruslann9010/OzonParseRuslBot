import sys
import asyncio
import logging

from browser_manager import BrowserManager
from parser import OzParserClient  # type: ignore
from database import DataBaseDb  # type: ignore
from queue_manager import RedisQueueManager

def setup_logging() -> None:
    """ Configures standard logging to display clean, 

        informative logs in the terminal.
    """
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout)])

async def main() -> None:
    """ Application entry point. Coordinates initialization and triggers the parser.
    """
    setup_logging()
    logging.info("Starting Ozon Scraper Application")

    await DataBaseDb.init_db()
    queue = RedisQueueManager()
    browser_client = BrowserManager()
    parser_client = OzParserClient(browser_client=browser_client)

    try:
        results = await parser_client.parse_results("ноутбук")
        
        for item in results:
            await queue.push_product(item)  
    finally:
        await browser_client.close()
        await queue.close()


if __name__ == "__main__":
    asyncio.run(main())