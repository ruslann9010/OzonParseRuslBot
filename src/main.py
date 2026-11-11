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
    """ Application entry point. 
    
    Coordinates initialization and triggers the parser.
    """
    setup_logging()
    logging.info("Starting Ozon Scraper Application")
    await DataBaseDb.init_db()
    queue_manager = RedisQueueManager()
    await queue_manager.connect()

    try:
        while True:
            task = await queue_manager.get_search_task()
            if not task: continue
            query = task["query"] 
            chat_id = task["chat_id"]
            logging.info(f"Получена задача на парсинг: '{query}' для чата {chat_id}")
            browser_client = BrowserManager()
            parser_client = OzParserClient(browser_client=browser_client)
            try:
                results = await parser_client.parse_results(query)
                for item in results:
                    await queue_manager.push_product(item)  
            except Exception as e:
                logging.error(f"Ошибка при парсинге запроса '{query}': {e}")  
            finally:
                await browser_client.close()          
    except  asyncio.CancelledError:
        logging.info("Воркер парсера остановлен.")
    finally:
        await queue_manager.close()


if __name__ == "__main__":
    asyncio.run(main())