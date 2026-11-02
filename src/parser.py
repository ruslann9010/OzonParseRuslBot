import logging
from typing import Optional
from playwright.async_api import Page


from browser_manager import BrowserManager
from network_utils import safe_goto


logger = logging.getLogger(__name__)

class OzParserClient:
    """ Main business logic layer for scraping data from Ozon.
    """

    def __init__(self, browser_client: BrowserManager) -> None:
        self.browser_manager = browser_client
        self.page: Optional[Page] = None


    async def parse_results(self, query: str) -> list[dict]:
      
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