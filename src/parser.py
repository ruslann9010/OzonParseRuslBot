"""Ozon marketplace scraping client for extracting product listings."""

import logging
from typing import Optional
from playwright.async_api import Page


from browser_manager import BrowserManager
from network_utils import safe_goto


logger = logging.getLogger(__name__)

class OzParserClient:
    """Main business logic layer for scraping product data from Ozon.

    Coordinates browser context creation, safe page navigation, DOM element
    extraction, and structuring of scraped product listings.

    Attributes:
        browser_manager (BrowserManager): Manager responsible for browser and
            context lifecycle.
        page (Optional[Page]): Active Playwright page instance used during a
            scraping session.
    """

    def __init__(self, browser_client: BrowserManager) -> None:
        """Initializes the Ozon parser client with a browser manager.

        Args:
            browser_client: Configured ``BrowserManager`` instance used to
                create isolated browser contexts.
        """
        self.browser_manager = browser_client
        self.page: Optional[Page] = None


    async def parse_results(self, query: str) -> list[dict]:
        """Navigates to Ozon search results for a query and extracts product cards.

        Creates a new browser context and page, loads the search results page,
        waits for product tile elements to render, and parses each card's
        title, price, and URL into a structured dictionary.

        Args:
            query: Search phrase or product keyword to look up on Ozon.

        Returns:
            A list of dictionaries, where each dictionary represents a scraped
            product (containing keys such as title, price, and url).
            Returns an empty list if navigation fails or no items are found.
        """
        parsed_data: list[dict] = []
        context = await self.browser_manager.create_context()
        self.page = await context.new_page()
        if not self.page:
            logger.error("Ошибка: Браузер не смог инициализировать страницу")
            return [] 
        succes = await safe_goto(self.page, query)
        if not succes:
            logger.error("Ошибка!!!!!!!!!!!!")
            await self.browser_manager.close()
            return[]
        try:
            await self.page.wait_for_load_state("networkidle")
            try:
                await self.page.wait_for_selector('div[class^="tile-root"]', timeout=5000)
            except Exception:
                logger.warning("Карточки товаров не появились на странице за 5 секунд.")
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
            await self.browser_manager.close()
        return parsed_data