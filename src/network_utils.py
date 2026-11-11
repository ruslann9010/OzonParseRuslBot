"""Network utility functions for safe page navigation and request throttling."""

import asyncio
import logging

from random import randint

from config import Config
from playwright.async_api import TimeoutError, Page


async def _human_delay() -> None:
    """Pauses execution for a random interval to mimic human browsing behavior.

    Introduces a non-blocking asynchronous delay between 2 and 5 seconds to
    reduce the likelihood of triggering anti-bot rate limits during retries.
    """
    await asyncio.sleep(randint(2, 5))    


async def safe_goto(page: Page, query: str) -> bool:
    """Navigates to the Ozon search results page with automatic retry handling.

    Constructs the search URL from the provided query and attempts to load the
    page up to Config.MAX_RETRIES times. If a timeout occurs, logs a
    warning and waits for a randomized human-like delay before retrying.

    Args:
        page: Active Playwright `Page` instance used for navigation.
        query: Product search phrase to append to the Ozon search URL.

    Returns:
        True if the page loaded successfully within the timeout limit; False if
        all retry attempts failed or an unexpected error occurred.
    """
    url = f"https://ozon.ru/search/?text={query}&from_global=true"

    for attempt in range(1, Config.MAX_RETRIES + 1):
        try:
            await page.goto(url, wait_until='networkidle', timeout=Config.PAGE_TIMEOUT)
            return True
        except TimeoutError:
            logging.warning(f"Ошибка: №{attempt} \r\n", exc_info=True)
            await _human_delay()
        except Exception as e:
            logging.error(f"Неизвестная ошибка! {e}")
    return False        



