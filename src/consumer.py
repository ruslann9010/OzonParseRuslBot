import asyncio
import logging
from queue_manager import RedisQueueManager
from database import DataBaseDb


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [CONSUMER] - %(levelname)s - %(message)s')


async def start_consumer():
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