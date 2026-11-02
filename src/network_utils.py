import asyncio
import logging

from random import randint

from config import Config
from playwright.async_api import TimeoutError, Page


async def _human_delay() -> None:
    await asyncio.sleep(randint(2, 5))    


async def safe_goto(page: Page, query: str) -> bool:

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



