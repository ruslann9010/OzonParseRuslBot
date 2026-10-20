import sys
import asyncio
import logging

from browser import OzBrowserClient
from parser import OzParserClient


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
    browser_client = OzBrowserClient()
    parser_client = OzParserClient(browser_client=browser_client)
    search_query = "ноутбук"
    logging.info(f"Triggering search parser for query: '{search_query}'")
    await parser_client.parse_results(query=search_query)
    logging.info("Application finished successfully.")


if __name__ == "__main__":
    asyncio.run(main())