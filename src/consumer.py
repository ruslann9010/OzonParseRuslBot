"""Asynchronous queue consumer for persisting scraped Ozon products to SQLite."""

import asyncio
import logging
from queue_manager import RedisQueueManager
from database import DataBaseDb


def setup_logging() -> None:
    """Configures root logging format and level for the consumer worker.

    Sets the logging threshold to ``INFO`` and formats log records with
    timestamps, the ``[CONSUMER]`` component tag, log levels, and messages.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [CONSUMER] - %(levelname)s - %(message)s')


async def start_consumer() -> None:
    """Initializes storage resources and continuously processes queued products.

    Ensures the SQLite database schema exists, connects to the Redis queue
    manager, and enters an infinite loop reading parsed product items via
    ``pop_product()``. Each valid item is persisted or updated in the database.
    Handles task cancellation and unexpected exceptions gracefully while
    guaranteeing Redis connection cleanup on exit.
    """
    setup_logging()
    logging.info("Инициализация консьюмера... Подключение к БД и Redis")
    await DataBaseDb.init_db()
    queue = RedisQueueManager()
    logging.info("Консьюмер успешно запущен и слушает очередь 'ozon_products'...")
    try:
        while True:
            product_data = await queue.pop_product()
            if product_data:
                logging.info(f"Получен товар из очереди: {product_data.get('title', '')[:30]}...")
                await DataBaseDb.save_or_update_product(product_data)            
    except asyncio.CancelledError:
        logging.info("Консьюмер останавливается...")
    except Exception as e:
        logging.error(f"Критическая ошибка в работе консьюмера: {e}", exc_info=True)
    finally:
        await queue.close()


if __name__ == "__main__":
    try:
        asyncio.run(start_consumer())
    except KeyboardInterrupt:
        print("\nКонсьюмер принудительно остановлен пользователем.") 