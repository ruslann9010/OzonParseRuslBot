import logging
import asyncio
from random import randint
from typing import Optional
from playwright.async_api import Page

from browser import OzBrowserClient  # type: ignore


logger = logging.getLogger(__name__)

class OzParserClient:
    """ Main business logic layer for scraping data from Ozon.
    """

    def __init__(self, browser_client: OzBrowserClient) -> None:
        self.client = browser_client
        self.page: Optional[Page] = None

    async def _human_delay(self) -> None:
        await asyncio.sleep(randint(2, 5))    

    async def parse_results(self, query: str) -> list[dict]:
        """ Searches for a specific query, waits for elements to load, and extracts data.
        """
        parsed_data: list[dict] = []
        self.page = await self.client.init_browser()
        if not self.page:
            logger.error("Ошибка: Браузер не смог инициализировать страницу")
            return []
        try:
            url = f"https://ozon.ru/search/?text={query}&from_global=true"
            logger.info(f"Navigating to search page for query: '{query}'")
            await self.page.goto(url, wait_until='networkidle', timeout=60000)
            await self._human_delay()
            card_locator = self.page.locator('div[class^="tile-root"]')
            cards = await card_locator.element_handles()

            for index, card in enumerate(cards, start=1):
                try:
                    title_element = await card.query_selector('span.tsBody500Medium')
                    if not title_element:
                        continue
                    product_title = await title_element.inner_text()       
                    price_element = await card.query_selector('span:has-text("₽")')
                    product_price = await price_element.inner_text() if price_element else "0"
                    link_element = await card.query_selector('a[class*="tile-clickable-element"]')
                    raw_href = await link_element.get_attribute("href") if link_element else ""
                    product_url = f"https://ozon.ru{raw_href}" if raw_href else "No URL"  
                    product_entry = {
                        "title": product_title.strip(),
                        "price": product_price.strip(),
                        "url": product_url
                    }
                    parsed_data.append(product_entry)
                    logger.info(f"[{index}/{len(cards)}] Parsed: {product_entry['title'][:30]}... | Price: {product_entry['price']}")
                except Exception as card_error:
                    logger.warning(f"Skipping individual card due to structure change: {card_error}")
                    continue   

            title_info = await self.page.title()
            logger.info(title_info)
        except Exception as e:
            logger.error(f"Error occurred during parsing process: {e}")
        finally:
            await self.client.close_browser()
        return parsed_data