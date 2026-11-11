"""Telegram bot interface for dispatching Ozon scraping tasks and querying results."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import asyncio
import logging

import aiohttp
from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession 

from src.config import Config 
from src.queue_manager import RedisQueueManager
from src.database import DataBaseDb

dp = Dispatcher()
queue_manager = RedisQueueManager()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [BOT] - %(levelname)s - %(message)s",
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROXY_URL = os.getenv("TG_PROXY_URL")

if not BOT_TOKEN:
    logging.critical("Ошибка: Токен бота не найден! Проверьте файл .env")
    sys.exit()

async def check_proxy(proxy_url: str) -> bool:
    """Verifies connectivity to Telegram servers through the specified HTTP proxy.

    Sends a lightweight GET request to ``https://telegram.org`` with a 5-second
    timeout to ensure the proxy is reachable and operational before starting
    bot polling.

    Args:
        proxy_url: Full proxy server URL (e.g., ``http://user:pass@host:port``).

    Returns:
        True if the proxy responds with HTTP status 200; False otherwise.
    """
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://telegram.org", proxy=proxy_url) as resp:
                return resp.status == 200
    except Exception:
        return False 


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handles the ``/start`` command by sending a welcome prompt to the user.

    Args:
        message: Incoming Telegram ``Message`` object triggering the command.
    """
    await message.answer(f"Напишите что хотите найти на озон")


@dp.message(Command("find"))
async def cmd_find(message: Message) -> None:
    """Handles the ``/find`` command by querying stored Ozon products from SQLite.

    Extracts the search keyword following ``/find``, fetches up to 10 matching
    products ordered by lowest price via ``DataBaseDb.get_products_by_query``,
    and sends a formatted summary back to the user.

    Args:
        message: Incoming Telegram ``Message`` containing the ``/find`` command
            and search query text.
    """
    if not message.text: return
    query =  message.text.replace("/find", "").strip()
    if not query:
        await message.answer("Укажите название товара после команды, например: /find ноутбук")
        return 
    products = await DataBaseDb.get_products_by_query(query, limit=10)
    if not products:
        await message.answer(f"По запросу «{query}» в базе пока ничего не найдено.")
        return
    lines = [f"📦 Результаты по запросу «{query}»:\n"]
    for idx, item in enumerate(products, start=1):
        lines.append(f"{idx}. {item['title']}\n💰 Цена: {item['price']} ₽\n🔗 {item['url']}\n")
    await message.answer("\n".join(lines), disable_web_page_preview=True)


@dp.message(F.text)
async def task_submission_parser(message: Message) -> None:
    """Enqueues plain-text user messages as new Ozon scraping tasks in Redis.

    Ignores slash-prefixed commands and pushes valid search phrases along with
    the user's ``chat_id`` into the Redis tasks queue for asynchronous scraping.

    Args:
        message: Incoming Telegram ``Message`` containing the user's search query.
    """
    if not message.text or message.text.startswith("/"): 
        return
    await queue_manager.push_search_task_queue(chat_id=message.chat.id, query=message.text.strip())
    await message.answer(f"🔍 Запрос«{message.text.strip()}»отправлен парсеру! Подождите 15–20 секунд и проверьте результаты:\n/find {message.text.strip()}")


async def main() -> None:
    """Initializes dependencies, configures proxy session, and starts bot polling.

    Validates the optional proxy connection, initializes the ``Bot`` instance
    with an ``AiohttpSession`` if a proxy is configured, connects to Redis,
    and runs ``dp.start_polling`` until interrupted, ensuring graceful cleanup
    of Redis and HTTP sessions on exit.
    """
    if PROXY_URL:
        if not await check_proxy(PROXY_URL):
            logging.critical(f"❌ Ошибка: Не валидный PROXY ({PROXY_URL}) просрочен или недоступен!")
            sys.exit()
        logging.info("✅ Прокси проверен")
        session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
        bot = Bot(token=str(BOT_TOKEN), session=session)
        try:
            await queue_manager.connect()
            await dp.start_polling(bot)
        except Exception as ex:
            logging.error(f"Ошибка при работе бота: {ex}")   
        finally: 
            await queue_manager.close()
            await bot.session.close()

if __name__ == "__main__": 
    asyncio.run(main())   
